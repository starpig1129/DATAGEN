import sys
import os

from src.system import MultiAgentSystem

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Main entry point"""
    system = MultiAgentSystem()
    
    # Example usage
    user_input = '''
    datapath:OnlineSalesData.csv
    Use machine learning to perform data analysis and write complete graphical reports
    '''
    system.run(user_input)

if __name__ == "__main__":
    main()
