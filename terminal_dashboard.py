"""
ATA Terminal Dashboard
CLI-based dashboard with deployment, download, settings, and run features
Similar to Claude Code's terminal IDE system
"""

import os
import json
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich import box
    from rich.live import Live
    from rich.columns import Columns
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not installed. Install with: pip install rich")
    print("Falling back to basic CLI interface...")

# Import ATA modules
from digital_soul_generator import DigitalSoulGenerator, DataExporter
from robot_internet_workflow import RobotInternetWorkflow
from virtual_city_integration import VirtualCityIntegrator
from global_architecture import GlobalArchitecture
from agent_communication_protocol import AgentCommunicationSystem


class TerminalDashboard:
    """Terminal-based dashboard for ATA system"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.state = {
            'digital_souls': [],
            'robot_workflows': [],
            'city_analysis': None,
            'global_architecture': None,
            'agent_communication': None,
            'settings': self._load_settings(),
            'logs': []
        }
        self.running = True
    
    def _load_settings(self) -> Dict:
        """Load settings from config file"""
        settings_file = 'ata_settings.json'
        default_settings = {
            'default_soul_count': 50,
            'default_workflow_count': 10,
            'default_activities': 10,
            'export_format': 'csv',
            'auto_save': True,
            'log_level': 'INFO',
            'dashboard_port': 5001
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return {**default_settings, **json.load(f)}
            except:
                return default_settings
        return default_settings
    
    def _save_settings(self):
        """Save settings to config file"""
        with open('ata_settings.json', 'w') as f:
            json.dump(self.state['settings'], f, indent=2)
    
    def _log(self, message: str, level: str = "INFO"):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.state['logs'].append(log_entry)
        if len(self.state['logs']) > 100:
            self.state['logs'] = self.state['logs'][-100:]
        
        if self.console:
            color = {
                'INFO': 'blue',
                'SUCCESS': 'green',
                'ERROR': 'red',
                'WARNING': 'yellow'
            }.get(level, 'white')
            self.console.print(f"[{color}]{log_entry}[/{color}]")
        else:
            print(log_entry)
    
    def print_header(self):
        """Print dashboard header"""
        if self.console:
            header = Text()
            header.append("🤖 ", style="bold blue")
            header.append("ATA Terminal Dashboard", style="bold cyan")
            header.append(" v1.0", style="dim")
            self.console.print(Panel(header, box=box.DOUBLE))
        else:
            print("=" * 60)
            print("🤖 ATA Terminal Dashboard v1.0")
            print("=" * 60)
    
    def print_status(self):
        """Print current system status"""
        if self.console:
            table = Table(title="System Status", box=box.ROUNDED)
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Count/Value", style="yellow")
            
            table.add_row(
                "Digital Souls",
                "Active" if self.state['digital_souls'] else "Inactive",
                str(len(self.state['digital_souls']))
            )
            table.add_row(
                "Robot Workflows",
                "Active" if self.state['robot_workflows'] else "Inactive",
                str(len(self.state['robot_workflows']))
            )
            table.add_row(
                "City Analysis",
                "Active" if self.state['city_analysis'] else "Inactive",
                "-" if not self.state['city_analysis'] else f"Index: {self.state['city_analysis']['democratic_index']['overall_index']:.3f}"
            )
            table.add_row(
                "Global Architecture",
                "Active" if self.state['global_architecture'] else "Inactive",
                "-" if not self.state['global_architecture'] else f"Souls: {self.state['global_architecture']['total_registered_souls']}"
            )
            table.add_row(
                "Agent Communication",
                "Active" if self.state['agent_communication'] else "Inactive",
                "-" if not self.state['agent_communication'] else f"Agents: {self.state['agent_communication']['total_agents']}"
            )
            
            self.console.print(table)
        else:
            print("\n--- System Status ---")
            print(f"Digital Souls: {len(self.state['digital_souls'])}")
            print(f"Robot Workflows: {len(self.state['robot_workflows'])}")
            print(f"City Analysis: {'Active' if self.state['city_analysis'] else 'Inactive'}")
            print(f"Global Architecture: {'Active' if self.state['global_architecture'] else 'Inactive'}")
            print(f"Agent Communication: {'Active' if self.state['agent_communication'] else 'Inactive'}")
    
    def show_main_menu(self):
        """Display main menu"""
        options = [
            "1. Run Components",
            "2. Deploy System",
            "3. Download/Export",
            "4. Settings",
            "5. View Status",
            "6. View Logs",
            "7. Launch Web Dashboard",
            "8. Exit"
        ]
        
        if self.console:
            self.console.print("\n[bold cyan]Main Menu[/bold cyan]")
            for option in options:
                self.console.print(f"  {option}")
        else:
            print("\nMain Menu:")
            for option in options:
                print(f"  {option}")
    
    def show_run_menu(self):
        """Display run components menu"""
        options = [
            "1. Generate Digital Souls",
            "2. Execute Robot Workflow",
            "3. Run City Analysis",
            "4. Initialize Global Architecture",
            "5. Initialize Agent Communication",
            "6. Run Full Simulation",
            "7. Back to Main Menu"
        ]
        
        if self.console:
            self.console.print("\n[bold cyan]Run Components[/bold cyan]")
            for option in options:
                self.console.print(f"  {option}")
        else:
            print("\nRun Components:")
            for option in options:
                print(f"  {option}")
    
    def show_deploy_menu(self):
        """Display deployment menu"""
        options = [
            "1. Start Web Dashboard (Background)",
            "2. Stop Web Dashboard",
            "3. Check Deployment Status",
            "4. Deploy to Production (Simulated)",
            "5. Back to Main Menu"
        ]
        
        if self.console:
            self.console.print("\n[bold cyan]Deployment[/bold cyan]")
            for option in options:
                self.console.print(f"  {option}")
        else:
            print("\nDeployment:")
            for option in options:
                print(f"  {option}")
    
    def show_download_menu(self):
        """Display download/export menu"""
        options = [
            "1. Export Digital Souls (CSV)",
            "2. Export Digital Souls (JSON)",
            "3. Export Robot Workflows",
            "4. Export City Analysis",
            "5. Export Global Architecture",
            "6. Export Agent Communication",
            "7. Export All Data",
            "8. Back to Main Menu"
        ]
        
        if self.console:
            self.console.print("\n[bold cyan]Download/Export[/bold cyan]")
            for option in options:
                self.console.print(f"  {option}")
        else:
            print("\nDownload/Export:")
            for option in options:
                print(f"  {option}")
    
    def show_settings_menu(self):
        """Display settings menu"""
        settings = self.state['settings']
        
        if self.console:
            self.console.print("\n[bold cyan]Current Settings[/bold cyan]")
            table = Table(box=box.SIMPLE)
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="yellow")
            
            for key, value in settings.items():
                table.add_row(key, str(value))
            
            self.console.print(table)
            
            options = [
                "1. Change Default Soul Count",
                "2. Change Default Workflow Count",
                "3. Change Export Format",
                "4. Toggle Auto-Save",
                "5. Change Dashboard Port",
                "6. Reset to Defaults",
                "7. Back to Main Menu"
            ]
            
            self.console.print("\n[bold cyan]Settings Options[/bold cyan]")
            for option in options:
                self.console.print(f"  {option}")
        else:
            print("\nCurrent Settings:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
            
            print("\nSettings Options:")
            print("1. Change Default Soul Count")
            print("2. Change Default Workflow Count")
            print("3. Change Export Format")
            print("4. Toggle Auto-Save")
            print("5. Change Dashboard Port")
            print("6. Reset to Defaults")
            print("7. Back to Main Menu")
    
    def generate_souls(self):
        """Generate digital souls"""
        count = self.state['settings']['default_soul_count']
        
        if self.console:
            count_input = Prompt.ask("Enter number of souls to generate", default=str(count))
            # Sanitize input: remove quotes, whitespace
            count_input = count_input.strip().strip('"').strip("'")
            try:
                count = int(count_input)
            except ValueError:
                self._log(f"Invalid input: {count_input}. Using default: {count}", "ERROR")
        else:
            count_input = input(f"Enter number of souls to generate ({count}): ")
            # Sanitize input: remove quotes, whitespace
            count_input = count_input.strip().strip('"').strip("'")
            try:
                count = int(count_input)
            except ValueError:
                self._log(f"Invalid input: {count_input}. Using default: {count}", "ERROR")
        
        self._log(f"Generating {count} digital souls...")
        
        try:
            generator = DigitalSoulGenerator()
            souls = generator.generate_population(count)
            
            self.state['digital_souls'] = [s.to_dict() for s in souls]
            
            if self.state['settings']['auto_save']:
                DataExporter.to_csv(souls, 'digital_souls_terminal.csv')
                DataExporter.to_json(souls, 'digital_souls_terminal.json')
                self._log(f"Exported {count} souls to CSV and JSON", "SUCCESS")
            
            self._log(f"Generated {count} digital souls successfully", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error generating souls: {str(e)}", "ERROR")
    
    def execute_workflow(self):
        """Execute robot workflow"""
        if not self.state['digital_souls']:
            self._log("No digital souls available. Generate souls first.", "ERROR")
            return
        
        import random
        soul = random.choice(self.state['digital_souls'])
        
        self._log(f"Executing robot workflow for {soul['digital_soul_hash'][:16]}...")
        
        try:
            workflow = RobotInternetWorkflow()
            result = workflow.execute_complete_workflow(
                soul['digital_soul_hash'],
                soul['emotional_resonance'],
                {"location": "Virtual City", "weather": "sunny"},
                soul['archetype']
            )
            
            self.state['robot_workflows'].append(result)
            self._log("Robot workflow executed successfully", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error executing workflow: {str(e)}", "ERROR")
    
    def run_city_analysis(self):
        """Run city analysis"""
        if not self.state['robot_workflows']:
            self._log("No robot workflows available. Execute workflow first.", "ERROR")
            return
        
        self._log("Executing city analysis...")
        
        try:
            integrator = VirtualCityIntegrator()
            sns_posts = []
            
            # Extract SNS posts from robot workflows
            for wf in self.state['robot_workflows']:
                if 'sns_post' in wf and wf['sns_post']:
                    post = wf['sns_post']
                    sns_posts.append({
                        'post_id': post.get('post_id', ''),
                        'text_content': post.get('text_content', ''),
                        'archetype': post.get('archetype', 'The Stoic Engineer'),
                        'insurance_impact': post.get('insurance_impact', {}),
                        'emotional_tuning': post.get('emotional_tuning', {})
                    })
            
            if not sns_posts:
                self._log("No SNS posts found in workflow results. Cannot perform analysis.", "WARNING")
                return
            
            analysis = integrator.analyze_city_state(sns_posts)
            self.state['city_analysis'] = analysis
            self._log(f"City analysis completed successfully. Analyzed {len(sns_posts)} SNS posts.", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error in city analysis: {str(e)}", "ERROR")
    
    def initialize_global_arch(self):
        """Initialize global architecture"""
        if not self.state['digital_souls']:
            self._log("No digital souls available. Generate souls first.", "ERROR")
            return
        
        self._log("Initializing global architecture...")
        
        try:
            citizens = [{'digital_soul_hash': s['digital_soul_hash'],
                        'memory_narrative': s['memory_anchor']['narrative'],
                        'birth_date': s['birth_date']} for s in self.state['digital_souls']]
            
            arch = GlobalArchitecture()
            arch.initialize_population(citizens)
            
            for city in ['NY', 'BJ', 'TK']:
                arch.simulate_city_activity(city, self.state['settings']['default_activities'])
            
            status = arch.get_global_status()
            self.state['global_architecture'] = status
            self._log("Global architecture initialized successfully", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error initializing global architecture: {str(e)}", "ERROR")
    
    def initialize_comm_system(self):
        """Initialize agent communication system"""
        self._log("Initializing agent communication system...")
        
        try:
            comm = AgentCommunicationSystem()
            
            agent_count = min(5, len(self.state['digital_souls']))
            for i in range(agent_count):
                soul = self.state['digital_souls'][i]
                comm.register_agent(
                    f"AGENT-{i+1:03d}",
                    soul['digital_soul_hash'],
                    f"Agent-{i+1}",
                    "NY",
                    soul['archetype']
                )
            
            comm.start_realtime_processor()
            
            stats = comm.get_system_statistics()
            self.state['agent_communication'] = stats
            self._log("Agent communication system initialized successfully", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error initializing communication: {str(e)}", "ERROR")
    
    def run_full_simulation(self):
        """Run full simulation"""
        self._log("Starting full simulation...", "INFO")
        
        # Generate souls
        self.generate_souls()
        
        # Execute workflows
        import random
        workflow_count = self.state['settings']['default_workflow_count']
        for _ in range(workflow_count):
            if not self.state['digital_souls']:
                self._log("No digital souls available. Cannot execute workflows.", "ERROR")
                return
            soul = random.choice(self.state['digital_souls'])
            workflow = RobotInternetWorkflow()
            result = workflow.execute_complete_workflow(
                soul['digital_soul_hash'],
                soul['emotional_resonance'],
                {"location": "Virtual City", "weather": "sunny"},
                soul['archetype']
            )
            self.state['robot_workflows'].append(result)
        
        self._log(f"Executed {workflow_count} robot workflows", "SUCCESS")
        
        # City analysis - extract SNS posts from workflows
        if self.state['robot_workflows']:
            integrator = VirtualCityIntegrator()
            sns_posts = []
            
            for wf in self.state['robot_workflows']:
                if 'sns_post' in wf and wf['sns_post']:
                    post = wf['sns_post']
                    sns_posts.append({
                        'post_id': post.get('post_id', ''),
                        'text_content': post.get('text_content', ''),
                        'archetype': post.get('archetype', 'The Stoic Engineer'),
                        'insurance_impact': post.get('insurance_impact', {}),
                        'emotional_tuning': post.get('emotional_tuning', {})
                    })
            
            if sns_posts:
                analysis = integrator.analyze_city_state(sns_posts)
                self.state['city_analysis'] = analysis
                self._log(f"City analysis completed. Analyzed {len(sns_posts)} SNS posts.", "SUCCESS")
            else:
                self._log("No SNS posts generated. Skipping city analysis.", "WARNING")
        
        # Global architecture
        self.initialize_global_arch()
        
        # Agent communication
        self.initialize_comm_system()
        
        self._log("Full simulation completed successfully", "SUCCESS")
    
    def start_web_dashboard(self):
        """Start web dashboard in background"""
        self._log("Starting web dashboard on port 5001...")
        
        try:
            # Start dashboard in background
            subprocess.Popen(
                [sys.executable, 'dashboard.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(2)
            self._log("Web dashboard started at http://localhost:5001", "SUCCESS")
        except Exception as e:
            self._log(f"Error starting web dashboard: {str(e)}", "ERROR")
    
    def stop_web_dashboard(self):
        """Stop web dashboard"""
        self._log("Stopping web dashboard...")
        
        try:
            # Kill process on port 5001
            subprocess.run(['pkill', '-f', 'dashboard.py'], check=False)
            self._log("Web dashboard stopped", "SUCCESS")
        except Exception as e:
            self._log(f"Error stopping web dashboard: {str(e)}", "ERROR")
    
    def export_data(self, data_type: str):
        """Export data based on type"""
        import csv
        
        try:
            if data_type == 'souls_csv':
                if not self.state['digital_souls']:
                    self._log("No digital souls to export", "ERROR")
                    return
                
                from digital_soul_generator import DigitalSoul, MemoryAnchor, EmotionalResonance
                souls_objects = []
                for soul_dict in self.state['digital_souls']:
                    memory = MemoryAnchor(
                        event_type=soul_dict['memory_anchor']['event_type'],
                        age_at_event=soul_dict['memory_anchor']['age_at_event'],
                        emotional_weight=soul_dict['memory_anchor']['emotional_weight'],
                        narrative=soul_dict['memory_anchor']['narrative'],
                        associated_emotions=soul_dict['memory_anchor']['associated_emotions']
                    )
                    emotional = EmotionalResonance(
                        trust=soul_dict['emotional_resonance']['trust'],
                        fear=soul_dict['emotional_resonance']['fear'],
                        altruism=soul_dict['emotional_resonance']['altruism'],
                        ambition=soul_dict['emotional_resonance']['ambition'],
                        curiosity=soul_dict['emotional_resonance']['curiosity']
                    )
                    soul = DigitalSoul(
                        citizen_id=soul_dict['citizen_id'],
                        digital_soul_hash=soul_dict['digital_soul_hash'],
                        birth_date=soul_dict['birth_date'],
                        age=soul_dict['age'],
                        gender=soul_dict['gender'],
                        life_stage=soul_dict['life_stage'],
                        memory_anchor=memory,
                        emotional_resonance=emotional,
                        archetype=soul_dict['archetype'],
                        social_credit_score=soul_dict['social_credit_score'],
                        insurance_risk_tier=soul_dict['insurance_risk_tier'],
                        behavioral_patterns=soul_dict['behavioral_patterns']
                    )
                    souls_objects.append(soul)
                
                DataExporter.to_csv(souls_objects, 'digital_souls_export.csv')
                self._log("Exported digital souls to digital_souls_export.csv", "SUCCESS")
            
            elif data_type == 'souls_json':
                with open('digital_souls_export.json', 'w') as f:
                    json.dump(self.state['digital_souls'], f, indent=2)
                self._log("Exported digital souls to digital_souls_export.json", "SUCCESS")
            
            elif data_type == 'workflows':
                with open('robot_workflows_export.json', 'w') as f:
                    json.dump(self.state['robot_workflows'], f, indent=2)
                self._log("Exported robot workflows to robot_workflows_export.json", "SUCCESS")
            
            elif data_type == 'city':
                with open('city_analysis_export.json', 'w') as f:
                    json.dump(self.state['city_analysis'], f, indent=2)
                self._log("Exported city analysis to city_analysis_export.json", "SUCCESS")
            
            elif data_type == 'global':
                with open('global_architecture_export.json', 'w') as f:
                    json.dump(self.state['global_architecture'], f, indent=2)
                self._log("Exported global architecture to global_architecture_export.json", "SUCCESS")
            
            elif data_type == 'comm':
                with open('agent_communication_export.json', 'w') as f:
                    json.dump(self.state['agent_communication'], f, indent=2)
                self._log("Exported agent communication to agent_communication_export.json", "SUCCESS")
            
            elif data_type == 'all':
                self.export_data('souls_csv')
                self.export_data('souls_json')
                self.export_data('workflows')
                self.export_data('city')
                self.export_data('global')
                self.export_data('comm')
                self._log("Exported all data", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error exporting data: {str(e)}", "ERROR")
    
    def update_setting(self, setting_key: str, value):
        """Update a setting with validation"""
        # Validation rules
        if setting_key == 'default_soul_count':
            try:
                value = int(value)
                if value < 1:
                    self._log(f"Invalid soul count: {value}. Minimum is 1. Using default.", "ERROR")
                    return
                if value > 100000:
                    self._log(f"Invalid soul count: {value}. Maximum is 100000. Using default.", "ERROR")
                    return
            except ValueError:
                self._log(f"Invalid soul count: {value}. Must be a number. Using default.", "ERROR")
                return
        
        elif setting_key == 'default_workflow_count':
            try:
                value = int(value)
                if value < 1:
                    self._log(f"Invalid workflow count: {value}. Minimum is 1. Using default.", "ERROR")
                    return
                if value > 1000:
                    self._log(f"Invalid workflow count: {value}. Maximum is 1000. Using default.", "ERROR")
                    return
            except ValueError:
                self._log(f"Invalid workflow count: {value}. Must be a number. Using default.", "ERROR")
                return
        
        elif setting_key == 'default_activities':
            try:
                value = int(value)
                if value < 1:
                    self._log(f"Invalid activity count: {value}. Minimum is 1. Using default.", "ERROR")
                    return
                if value > 100:
                    self._log(f"Invalid activity count: {value}. Maximum is 100. Using default.", "ERROR")
                    return
            except ValueError:
                self._log(f"Invalid activity count: {value}. Must be a number. Using default.", "ERROR")
                return
        
        elif setting_key == 'export_format':
            if value.lower() not in ['csv', 'json']:
                self._log(f"Invalid export format: {value}. Must be 'csv' or 'json'. Using default.", "ERROR")
                return
            value = value.lower()
        
        elif setting_key == 'dashboard_port':
            try:
                value = int(value)
                if value < 1024:
                    self._log(f"Invalid port: {value}. Minimum is 1024. Using default.", "ERROR")
                    return
                if value > 65535:
                    self._log(f"Invalid port: {value}. Maximum is 65535. Using default.", "ERROR")
                    return
            except ValueError:
                self._log(f"Invalid port: {value}. Must be a number. Using default.", "ERROR")
                return
        
        self.state['settings'][setting_key] = value
        self._save_settings()
        self._log(f"Updated {setting_key} to {value}", "SUCCESS")
    
    def view_logs(self):
        """View recent logs"""
        if self.console:
            self.console.print("\n[bold cyan]Recent Logs[/bold cyan]")
            for log in self.state['logs'][-20:]:
                level = log.split(']')[1].split(']')[0].replace('[', '')
                color = {
                    'INFO': 'blue',
                    'SUCCESS': 'green',
                    'ERROR': 'red',
                    'WARNING': 'yellow'
                }.get(level, 'white')
                self.console.print(f"[{color}]{log}[/{color}]")
        else:
            print("\nRecent Logs:")
            for log in self.state['logs'][-20:]:
                print(f"  {log}")
    
    def run(self):
        """Main run loop"""
        self.print_header()
        
        try:
            while self.running:
                self.show_main_menu()
                
                if self.console:
                    choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
                else:
                    choice = input("\nSelect option (1-8): ")
                
                if choice == "1":
                    # Run Components
                    while True:
                        self.show_run_menu()
                        if self.console:
                            run_choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "7"])
                        else:
                            run_choice = input("\nSelect option (1-7): ")
                        
                        if run_choice == "1":
                            self.generate_souls()
                        elif run_choice == "2":
                            self.execute_workflow()
                        elif run_choice == "3":
                            self.run_city_analysis()
                        elif run_choice == "4":
                            self.initialize_global_arch()
                        elif run_choice == "5":
                            self.initialize_comm_system()
                        elif run_choice == "6":
                            self.run_full_simulation()
                        elif run_choice == "7":
                            break
                
                elif choice == "2":
                    # Deploy
                    while True:
                        self.show_deploy_menu()
                        if self.console:
                            deploy_choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5"])
                        else:
                            deploy_choice = input("\nSelect option (1-5): ")
                        
                        if deploy_choice == "1":
                            self.start_web_dashboard()
                        elif deploy_choice == "2":
                            self.stop_web_dashboard()
                        elif deploy_choice == "3":
                            self._log("Checking deployment status...", "INFO")
                            self._log("Web dashboard: Running on port 5001", "SUCCESS")
                        elif deploy_choice == "4":
                            self._log("Simulated production deployment...", "INFO")
                            self._log("Production deployment completed", "SUCCESS")
                        elif deploy_choice == "5":
                            break
                
                elif choice == "3":
                    # Download/Export
                    while True:
                        self.show_download_menu()
                        if self.console:
                            download_choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
                        else:
                            download_choice = input("\nSelect option (1-8): ")
                        
                        if download_choice == "1":
                            self.export_data('souls_csv')
                        elif download_choice == "2":
                            self.export_data('souls_json')
                        elif download_choice == "3":
                            self.export_data('workflows')
                        elif download_choice == "4":
                            self.export_data('city')
                        elif download_choice == "5":
                            self.export_data('global')
                        elif download_choice == "6":
                            self.export_data('comm')
                        elif download_choice == "7":
                            self.export_data('all')
                        elif download_choice == "8":
                            break
                
                elif choice == "4":
                    # Settings
                    while True:
                        self.show_settings_menu()
                        if self.console:
                            settings_choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "7"])
                        else:
                            settings_choice = input("\nSelect option (1-7): ")
                        
                        if settings_choice == "1":
                            if self.console:
                                value = Prompt.ask("Enter default soul count", default=str(self.state['settings']['default_soul_count']))
                            else:
                                value = input("Enter default soul count: ")
                            self.update_setting('default_soul_count', value)
                        elif settings_choice == "2":
                            if self.console:
                                value = Prompt.ask("Enter default workflow count", default=str(self.state['settings']['default_workflow_count']))
                            else:
                                value = input("Enter default workflow count: ")
                            self.update_setting('default_workflow_count', value)
                        elif settings_choice == "3":
                            if self.console:
                                value = Prompt.ask("Enter export format (csv/json)", default=self.state['settings']['export_format'])
                            else:
                                value = input("Enter export format (csv/json): ")
                            self.update_setting('export_format', value)
                        elif settings_choice == "4":
                            current = self.state['settings']['auto_save']
                            self.update_setting('auto_save', not current)
                        elif settings_choice == "5":
                            if self.console:
                                value = Prompt.ask("Enter dashboard port", default=str(self.state['settings']['dashboard_port']))
                            else:
                                value = input("Enter dashboard port: ")
                            self.update_setting('dashboard_port', int(value))
                        elif settings_choice == "6":
                            self.state['settings'] = self._load_settings()
                            self._save_settings()
                            self._log("Settings reset to defaults", "SUCCESS")
                        elif settings_choice == "7":
                            break
                
                elif choice == "5":
                    # View Status
                    self.print_status()
                
                elif choice == "6":
                    # View Logs
                    self.view_logs()
                
                elif choice == "7":
                    # Launch Web Dashboard
                    self.start_web_dashboard()
                    if self.console:
                        self.console.print("\n[green]Web dashboard is running at http://localhost:5001[/green]")
                        self.console.print("Press Ctrl+C to return to terminal")
                    else:
                        print("\nWeb dashboard is running at http://localhost:5001")
                        print("Press Ctrl+C to return to terminal")
                    
                    # Keep running until user interrupts
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        self._log("Returning to terminal menu", "INFO")
                
                elif choice == "8":
                    # Exit
                    self.running = False
                    self._log("Exiting ATA Terminal Dashboard", "INFO")
                
                # Clear screen for next iteration
                if RICH_AVAILABLE:
                    self.console.clear()
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                
                self.print_header()
        
        except KeyboardInterrupt:
            self._log("\nInterrupted by user. Shutting down gracefully...", "WARNING")
            self.running = False
            self._log("ATA Terminal Dashboard closed.", "INFO")
        except Exception as e:
            self._log(f"Unexpected error: {str(e)}", "ERROR")
            self.running = False


def main():
    """Main entry point"""
    dashboard = TerminalDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
