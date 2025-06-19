import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class ScheduleVisualizer:
    def __init__(self):
        pass # No need for pre-defined colors here
    
    def create_gantt_chart(self, schedule_df):
        """Create a Gantt chart from the schedule DataFrame."""
        # Prepare data for Gantt chart
        tasks = []
        unique_jobs = sorted(schedule_df['JobID'].unique())
        
        # Define a palette of colors for jobs. Expand if more jobs are expected.
        # These are a few distinct colors, you can add more.
        color_palette = [
            'rgb(46, 137, 205)', 'rgb(114, 44, 121)', 'rgb(198, 47, 105)',
            'rgb(58, 149, 136)', 'rgb(107, 127, 135)', 'rgb(255, 165, 0)',
            'rgb(0, 128, 0)', 'rgb(128, 0, 128)', 'rgb(255, 0, 0)',
            'rgb(0, 255, 0)', 'rgb(0, 0, 255)', 'rgb(255, 255, 0)'
        ]

        # Create a dictionary to map JobID to colors
        job_colors = {}
        for i, job_id in enumerate(unique_jobs):
            job_colors[f"Job {job_id}"] = color_palette[i % len(color_palette)]

        for _, row in schedule_df.iterrows():
            tasks.append(dict(
                Task=f"Machine {row['MachineID']}",
                Start=row['Start'],
                Finish=row['End'],
                Resource=f"Job {row['JobID']}",
                Description=f"Task {row['TaskID']}"
            ))
        
        # Create Gantt chart using the dynamically generated job_colors
        fig = ff.create_gantt(
            tasks,
            colors=job_colors,
            index_col='Resource',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True
        )
        
        # Update layout
        fig.update_layout(
            title='Job Shop Schedule',
            xaxis_title='Time',
            yaxis_title='Machine',
            height=400,
            font=dict(size=10)
        )
        
        return fig
    
    def create_utilization_chart(self, utilization_dict):
        """Create a bar chart showing machine utilization rates."""
        machines = list(utilization_dict.keys())
        utilization = [rate * 100 for rate in utilization_dict.values()]
        
        fig = go.Figure(data=[
            go.Bar(
                x=machines,
                y=utilization,
                text=[f'{u:.1f}%' for u in utilization],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Machine Utilization Rates',
            xaxis_title='Machine',
            yaxis_title='Utilization Rate (%)',
            yaxis_range=[0, 100],
            height=400
        )
        
        return fig
    
    def create_comparison_chart(self, before_util, after_util):
        """Create a comparison chart of utilization rates before and after optimization."""
        machines = list(before_util.keys())
        before = [rate * 100 for rate in before_util.values()]
        after = [rate * 100 for rate in after_util.values()]
        
        fig = go.Figure(data=[
            go.Bar(
                name='Before Optimization',
                x=machines,
                y=before,
                text=[f'{u:.1f}%' for u in before],
                textposition='auto',
            ),
            go.Bar(
                name='After Optimization',
                x=machines,
                y=after,
                text=[f'{u:.1f}%' for u in after],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Machine Utilization Comparison',
            xaxis_title='Machine',
            yaxis_title='Utilization Rate (%)',
            yaxis_range=[0, 100],
            barmode='group',
            height=400
        )
        
        return fig 