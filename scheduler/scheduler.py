from ortools.sat.python import cp_model
import pandas as pd
import numpy as np

class JobShopScheduler:
    def __init__(self):
        self.model = None
        self.solver = None
        self.jobs_data = None
        self.machines = None
        self.jobs = None
        self.horizon = None
        
    def load_data(self, csv_path):
        """Load job data from CSV file or file-like object."""
        if hasattr(csv_path, 'read'):
            csv_path.seek(0)
            self.jobs_data = pd.read_csv(csv_path)
        else:
            self.jobs_data = pd.read_csv(str(csv_path))

        # Ensure Deadline column exists, fill with horizon if not present
        if 'Deadline' not in self.jobs_data.columns:
            self.jobs_data['Deadline'] = np.nan # Temporarily fill with NaN

        print(f"Jobs Data Head:\n{self.jobs_data.head()}")
        print(f"Jobs Data is Empty: {self.jobs_data.empty}")
        self.machines = sorted(self.jobs_data['MachineID'].unique())
        self.jobs = sorted(self.jobs_data['JobID'].unique())

        # Calculate horizon based on total duration, then use it for missing deadlines
        self.horizon = int(self.jobs_data['Duration'].sum())
        self.jobs_data['Deadline'] = self.jobs_data['Deadline'].fillna(self.horizon).astype(int)
        
    def create_model(self):
        """Create the constraint programming model."""
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Create variables
        all_tasks = {}
        machine_to_intervals = {machine: [] for machine in self.machines}
        
        for _, task in self.jobs_data.iterrows():
            job_id = task['JobID']
            task_id = task['TaskID']
            machine_id = task['MachineID']
            duration = task['Duration']
            
            suffix = f'_{job_id}_{task_id}'
            
            # Create interval variable
            start_var = self.model.NewIntVar(0, self.horizon, f'start{suffix}')
            end_var = self.model.NewIntVar(0, self.horizon, f'end{suffix}')
            interval_var = self.model.NewIntervalVar(
                start_var, duration, end_var, f'interval{suffix}')
            
            all_tasks[job_id, task_id] = {
                'start': start_var,
                'end': end_var,
                'interval': interval_var,
                'machine': machine_id
            }
            
            machine_to_intervals[machine_id].append(interval_var)
        
        # Add constraints
        # 1. No overlap between tasks on same machine
        for machine in self.machines:
            self.model.AddNoOverlap(machine_to_intervals[machine])
        
        # 2. Task precedence within jobs
        for job in self.jobs:
            job_tasks = self.jobs_data[self.jobs_data['JobID'] == job].sort_values('TaskID')
            for i in range(len(job_tasks) - 1):
                current_task = (job, job_tasks.iloc[i]['TaskID'])
                next_task = (job, job_tasks.iloc[i + 1]['TaskID'])
                self.model.Add(
                    all_tasks[current_task]['end'] <= all_tasks[next_task]['start']
                )
        
        # 3. Minimize makespan
        obj_var = self.model.NewIntVar(0, self.horizon, 'makespan')
        self.model.AddMaxEquality(
            obj_var,
            [all_tasks[job, task]['end'] for job in self.jobs
             for task in self.jobs_data[self.jobs_data['JobID'] == job]['TaskID']]
        )

        # Add soft constraints for deadlines (bonus feature)
        # We will add a penalty for each unit of time a job finishes after its deadline.
        # This creates a combined objective of minimizing makespan and deadline tardiness.
        objective_terms = [obj_var]
        for job_id in self.jobs:
            job_tasks = self.jobs_data[self.jobs_data['JobID'] == job_id]
            job_deadline = job_tasks['Deadline'].iloc[0] # Assuming one deadline per job

            # Find the end time of the last task for this job
            last_task_end = self.model.NewIntVar(0, self.horizon, f'job_{job_id}_end')
            self.model.AddMaxEquality(last_task_end,
                                      [all_tasks[job_id, task_id]['end'] for task_id in job_tasks['TaskID']])

            # Calculate tardiness: max(0, last_task_end - job_deadline)
            tardiness = self.model.NewIntVar(0, self.horizon, f'job_{job_id}_tardiness')
            self.model.AddMaxEquality(tardiness, [last_task_end - job_deadline, 0])

            # Add tardiness to the objective with a weight (e.g., 1 to make it equally important as makespan)
            # You can adjust this weight (e.g., 5 or 10) to make meeting deadlines more critical.
            objective_terms.append(tardiness)

        self.model.Minimize(sum(objective_terms))
        
        print(f"Number of tasks created in model: {len(all_tasks)}")
        self.all_tasks = all_tasks # Store all_tasks as a class member
        
    def solve(self):
        """Solve the scheduling problem."""
        if not self.model:
            raise ValueError("Model not created. Call create_model() first.")
        
        # The model has already been created and all_tasks populated by create_model()
        # all_tasks = self.create_model() # REMOVE THIS LINE
        
        # Solve the model
        status = self.solver.Solve(self.model)
        print(f"Solver status: {self.solver.StatusName(status)}")
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            solution = []
            for job in self.jobs:
                for task in self.jobs_data[self.jobs_data['JobID'] == job]['TaskID']:
                    task_data = self.all_tasks[job, task] # Access from self.all_tasks
                    solution.append({
                        'JobID': job,
                        'TaskID': task,
                        'MachineID': task_data['machine'],
                        'Start': self.solver.Value(task_data['start']),
                        'End': self.solver.Value(task_data['end']),
                        'Duration': self.jobs_data[
                            (self.jobs_data['JobID'] == job) & 
                            (self.jobs_data['TaskID'] == task)
                        ]['Duration'].iloc[0],
                        'Deadline': self.jobs_data[
                            (self.jobs_data['JobID'] == job)
                        ]['Deadline'].iloc[0] # Add deadline to solution for potential display
                    })
            
            solution_df = pd.DataFrame(solution)
            print(f"Solution DataFrame Head:\n{solution_df.head()}")
            return solution_df
        else:
            raise Exception('No solution found.')
    
    def get_makespan(self):
        """Get the makespan (total completion time) of the solution."""
        if not self.solver:
            raise ValueError("Problem not solved. Call solve() first.")
        return self.solver.ObjectiveValue()
    
    def get_initial_machine_utilization(self):
        """Calculate initial machine utilization rates based on task durations."""
        machine_durations = self.jobs_data.groupby('MachineID')['Duration'].sum()
        total_time = self.horizon
        if total_time == 0:
            return {machine: 0.0 for machine in self.machines}
        return (machine_durations / total_time).to_dict()

    def get_optimized_machine_utilization(self, schedule_df):
        """Calculate machine utilization rates from the optimized schedule."""
        total_time = self.horizon
        machine_times = schedule_df.groupby('MachineID').apply(
            lambda x: (x['End'] - x['Start']).sum()
        )
        if total_time == 0:
            return {machine: 0.0 for machine in self.machines}
        return (machine_times / total_time).to_dict() 