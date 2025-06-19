import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scheduler.scheduler import JobShopScheduler
from visualization.visualizer import ScheduleVisualizer

st.set_page_config(
    page_title="Smart AI Job-Shop Scheduler",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("🚀 Smart AI Job-Shop Scheduler for SMEs")
    st.markdown("""
    Optimize your job scheduling with AI to enhance machine utilization and meet deadlines.
    
    --- 
    """)
    
    # --- Sidebar for Controls ---
    st.sidebar.header("⚙️ Configuration")
    
    # File upload in sidebar
    uploaded_file = st.sidebar.file_uploader(
        "Upload your job data (CSV)",
        type=['csv'],
        help="CSV should have columns: JobID, TaskID, MachineID, Duration, and optional Deadline."
    )
    
    # Use sample data if no file uploaded
    csv_path = None # Initialize to None
    if uploaded_file is None:
        st.sidebar.info("No file uploaded. Using sample data.")
        csv_path = "data/sample_jobs.csv"
    else:
        st.sidebar.success("CSV file uploaded successfully!")
        csv_path = uploaded_file
    
    # Initialize scheduler and visualizer
    scheduler = JobShopScheduler()
    visualizer = ScheduleVisualizer()
    
    # Check if csv_path is set before attempting to load data
    if csv_path:
        try:
            # Load and display data in an expander
            scheduler.load_data(csv_path)
            with st.expander("📂 View Input Data", expanded=True):
                st.subheader("Loaded Job Data")
                st.dataframe(scheduler.jobs_data)
            
            # Run Optimizer button in sidebar
            if st.sidebar.button("✨ Run Optimizer"):
                with st.spinner("Optimizing schedule..."):
                    scheduler.create_model()
                    schedule_df = scheduler.solve()
                    makespan = scheduler.get_makespan()
                    
                    # Calculate utilization rates
                    before_util = scheduler.get_initial_machine_utilization()
                    after_util = scheduler.get_optimized_machine_utilization(schedule_df)
                    
                    # --- Optimization Results Section ---
                    st.header("📈 Optimization Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Total Completion Time (Makespan)", value=f"{makespan:.1f} time units", delta="Lower is better")
                    
                    # Calculate percentage improvement for utilization
                    initial_total_util = sum(before_util.values()) / len(before_util) if before_util else 0
                    optimized_total_util = sum(after_util.values()) / len(after_util) if after_util else 0
                    
                    util_improvement_percent = 0
                    if initial_total_util > 0:
                        util_improvement_percent = ((optimized_total_util - initial_total_util) / initial_total_util) * 100
                    
                    with col2:
                        st.metric(label="Average Machine Utilization", 
                                  value=f"{optimized_total_util*100:.1f}%", 
                                  delta=f"{util_improvement_percent:.1f}% vs Initial", 
                                  delta_color="normal")
                    
                    st.markdown("--- ")
                    
                    # Display Gantt chart in an expander
                    with st.expander("📊 Optimized Schedule Gantt Chart", expanded=True):
                        st.subheader("Gantt Chart")
                        gantt_fig = visualizer.create_gantt_chart(schedule_df)
                        st.plotly_chart(gantt_fig, use_container_width=True)
                        st.info("Each colored bar represents a job task. The x-axis is time, and the y-axis shows machines.")
                    
                    # Display utilization comparison in an expander
                    with st.expander("📉 Machine Utilization Analysis", expanded=True):
                        st.subheader("Utilization Comparison (Before vs After Optimization)")
                        util_fig = visualizer.create_comparison_chart(before_util, after_util)
                        st.plotly_chart(util_fig, use_container_width=True)
                        st.info("See how machine utilization rates improve after optimization.")
                    
                    # Display detailed schedule in an expander
                    with st.expander("📋 Detailed Optimized Schedule", expanded=False):
                        st.subheader("Detailed Schedule Table")
                        st.dataframe(schedule_df.sort_values(['MachineID', 'Start']))
                        st.info("Scroll to view the exact start, end, and duration for each task.")
                    
        except Exception as e:
            st.error(f"🚫 An error occurred: {str(e)}")
            st.info("💡 Please make sure your CSV file follows the required format (JobID, TaskID, MachineID, Duration, [Deadline]).")
    else:
        st.warning("Please upload a CSV file or ensure the sample data path is correct.")

if __name__ == "__main__":
    main() 