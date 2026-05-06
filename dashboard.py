"""
ATA Integrated Dashboard
Web-based dashboard integrating all ATA components:
- Digital Soul Generator
- Robot-to-Internet Workflow
- Virtual City Integration
- Global Architecture
- Agent Communication Protocol
"""

import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Import ATA modules
from digital_soul_generator import DigitalSoulGenerator, DataExporter
from robot_internet_workflow import RobotInternetWorkflow
from virtual_city_integration import VirtualCityIntegrator
from global_architecture import GlobalArchitecture
from agent_communication_protocol import AgentCommunicationSystem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ata-dashboard-secret-key-2024'

# Global state for dashboard
dashboard_state = {
    'digital_souls': [],
    'robot_workflows': [],
    'city_analysis': None,
    'global_architecture': None,
    'agent_communication': None,
    'simulation_running': False,
    'logs': []
}


class DashboardLogger:
    """Logger for dashboard events"""
    
    @staticmethod
    def log(message: str, level: str = "INFO"):
        """Log a message to the dashboard"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        dashboard_state['logs'].append(log_entry)
        # Keep only last 100 logs
        if len(dashboard_state['logs']) > 100:
            dashboard_state['logs'] = dashboard_state['logs'][-100:]
        print(f"[{level}] {message}")


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get overall system status"""
    return jsonify({
        'status': 'running',
        'digital_souls_count': len(dashboard_state['digital_souls']),
        'robot_workflows_count': len(dashboard_state['robot_workflows']),
        'city_analysis_active': dashboard_state['city_analysis'] is not None,
        'global_architecture_active': dashboard_state['global_architecture'] is not None,
        'agent_communication_active': dashboard_state['agent_communication'] is not None,
        'simulation_running': dashboard_state['simulation_running'],
        'logs_count': len(dashboard_state['logs'])
    })


@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    return jsonify(dashboard_state['logs'][-20:])


# Digital Soul Generator Endpoints
@app.route('/api/digital-souls/generate', methods=['POST'])
def generate_digital_souls():
    """Generate digital souls"""
    try:
        count = request.json.get('count', 10)
        DashboardLogger.log(f"Generating {count} digital souls...")
        
        generator = DigitalSoulGenerator()
        new_souls = generator.generate_population(count)
        
        # Convert to dict for storage
        for soul in new_souls:
            dashboard_state['digital_souls'].append(soul.to_dict())
        
        DashboardLogger.log(f"Generated {count} digital souls successfully", "SUCCESS")
        
        return jsonify({
            'success': True,
            'count': count,
            'total': len(dashboard_state['digital_souls']),
            'souls': [s.to_dict() for s in new_souls]
        })
    except Exception as e:
        DashboardLogger.log(f"Error generating digital souls: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/digital-souls')
def get_digital_souls():
    """Get all digital souls"""
    limit = request.args.get('limit', 50, type=int)
    souls = dashboard_state['digital_souls'][-limit:]
    return jsonify({
        'count': len(souls),
        'total': len(dashboard_state['digital_souls']),
        'souls': souls
    })


@app.route('/api/digital-souls/export', methods=['POST'])
def export_digital_souls():
    """Export digital souls to CSV"""
    try:
        filename = request.json.get('filename', 'digital_souls_dashboard.csv')
        
        # Convert dict back to DigitalSoul objects for export
        from digital_soul_generator import DigitalSoul, MemoryAnchor, EmotionalResonance
        souls_objects = []
        for soul_dict in dashboard_state['digital_souls']:
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
        
        DataExporter.to_csv(souls_objects, filename)
        DashboardLogger.log(f"Exported {len(souls_objects)} digital souls to {filename}", "SUCCESS")
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        DashboardLogger.log(f"Error exporting digital souls: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/digital-souls/statistics')
def get_digital_souls_statistics():
    """Get statistics about digital souls"""
    if not dashboard_state['digital_souls']:
        return jsonify({'error': 'No digital souls generated yet'})
    
    souls = dashboard_state['digital_souls']
    
    # Archetype distribution
    archetype_counts = {}
    for soul in souls:
        arch = soul['archetype']
        archetype_counts[arch] = archetype_counts.get(arch, 0) + 1
    
    # Age distribution
    age_groups = {'16-24': 0, '25-34': 0, '35-44': 0, '45-54': 0, '55-64': 0, '65+': 0}
    for soul in souls:
        age = soul['age']
        if age < 25:
            age_groups['16-24'] += 1
        elif age < 35:
            age_groups['25-34'] += 1
        elif age < 45:
            age_groups['35-44'] += 1
        elif age < 55:
            age_groups['45-54'] += 1
        elif age < 65:
            age_groups['55-64'] += 1
        else:
            age_groups['65+'] += 1
    
    # Risk tier distribution
    risk_tiers = {}
    for soul in souls:
        tier = soul['insurance_risk_tier']
        risk_tiers[tier] = risk_tiers.get(tier, 0) + 1
    
    # Average emotional values
    avg_emotions = {
        'trust': sum(s['emotional_resonance']['trust'] for s in souls) / len(souls),
        'fear': sum(s['emotional_resonance']['fear'] for s in souls) / len(souls),
        'altruism': sum(s['emotional_resonance']['altruism'] for s in souls) / len(souls),
        'ambition': sum(s['emotional_resonance']['ambition'] for s in souls) / len(souls),
        'curiosity': sum(s['emotional_resonance']['curiosity'] for s in souls) / len(souls)
    }
    
    return jsonify({
        'total': len(souls),
        'archetype_distribution': archetype_counts,
        'age_distribution': age_groups,
        'risk_tier_distribution': risk_tiers,
        'average_emotions': avg_emotions
    })


# Robot Workflow Endpoints
@app.route('/api/robot-workflow/execute', methods=['POST'])
def execute_robot_workflow():
    """Execute robot-to-internet workflow"""
    try:
        if not dashboard_state['digital_souls']:
            return jsonify({'success': False, 'error': 'No digital souls available. Generate souls first.'})
        
        # Use a random soul
        soul = random.choice(dashboard_state['digital_souls'])
        digital_soul_hash = soul['digital_soul_hash']
        archetype = soul['archetype']
        emotional_vector = soul['emotional_resonance']
        
        DashboardLogger.log(f"Executing robot workflow for {digital_soul_hash[:16]}...")
        
        workflow = RobotInternetWorkflow()
        environmental_context = {
            "location": "Virtual City",
            "weather": "sunny",
            "time_of_day": "afternoon"
        }
        
        result = workflow.execute_complete_workflow(
            digital_soul_hash, emotional_vector, environmental_context, archetype
        )
        
        dashboard_state['robot_workflows'].append(result)
        DashboardLogger.log("Robot workflow executed successfully", "SUCCESS")
        
        return jsonify({
            'success': True,
            'workflow_id': result['workflow_id'],
            'result': result
        })
    except Exception as e:
        DashboardLogger.log(f"Error executing robot workflow: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/robot-workflows')
def get_robot_workflows():
    """Get robot workflow history"""
    limit = request.args.get('limit', 10, type=int)
    workflows = dashboard_state['robot_workflows'][-limit:]
    return jsonify({
        'count': len(workflows),
        'total': len(dashboard_state['robot_workflows']),
        'workflows': workflows
    })


# Virtual City Integration Endpoints
@app.route('/api/city-analysis/execute', methods=['POST'])
def execute_city_analysis():
    """Execute virtual city analysis"""
    try:
        if not dashboard_state['robot_workflows']:
            return jsonify({'success': False, 'error': 'No robot workflows available. Execute workflow first.'})
        
        DashboardLogger.log("Executing virtual city analysis...")
        
        # Extract SNS posts from workflow results
        integrator = VirtualCityIntegrator()
        sns_posts = []
        
        for wf in dashboard_state['robot_workflows']:
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
            DashboardLogger.log("No SNS posts found in workflow results", "WARNING")
            return jsonify({'success': False, 'error': 'No SNS posts generated from workflows'})
        
        analysis_result = integrator.analyze_city_state(sns_posts)
        
        dashboard_state['city_analysis'] = analysis_result
        DashboardLogger.log(f"Virtual city analysis completed. Analyzed {len(sns_posts)} SNS posts.", "SUCCESS")
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'posts_analyzed': len(sns_posts)
        })
    except Exception as e:
        DashboardLogger.log(f"Error executing city analysis: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/city-analysis')
def get_city_analysis():
    """Get city analysis results"""
    if dashboard_state['city_analysis'] is None:
        return jsonify({'error': 'No city analysis available'})
    return jsonify(dashboard_state['city_analysis'])


# Global Architecture Endpoints
@app.route('/api/global-architecture/initialize', methods=['POST'])
def initialize_global_architecture():
    """Initialize global architecture"""
    try:
        if not dashboard_state['digital_souls']:
            return jsonify({'success': False, 'error': 'No digital souls available. Generate souls first.'})
        
        DashboardLogger.log("Initializing global architecture...")
        
        # Convert souls to required format
        citizens = []
        for soul in dashboard_state['digital_souls']:
            citizens.append({
                'digital_soul_hash': soul['digital_soul_hash'],
                'memory_narrative': soul['memory_anchor']['narrative'],
                'birth_date': soul['birth_date']
            })
        
        architecture = GlobalArchitecture()
        architecture.initialize_population(citizens)
        
        # Simulate some activities
        for city in ['NY', 'BJ', 'TK']:
            architecture.simulate_city_activity(city, 10)
        
        status = architecture.get_global_status()
        
        dashboard_state['global_architecture'] = status
        DashboardLogger.log("Global architecture initialized successfully", "SUCCESS")
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        DashboardLogger.log(f"Error initializing global architecture: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/global-architecture')
def get_global_architecture():
    """Get global architecture status"""
    if dashboard_state['global_architecture'] is None:
        return jsonify({'error': 'Global architecture not initialized'})
    return jsonify(dashboard_state['global_architecture'])


# Agent Communication Endpoints
@app.route('/api/agent-communication/initialize', methods=['POST'])
def initialize_agent_communication():
    """Initialize agent communication system"""
    try:
        DashboardLogger.log("Initializing agent communication system...")
        
        comm_system = AgentCommunicationSystem()
        
        # Register some agents from digital souls
        agent_count = min(5, len(dashboard_state['digital_souls']))
        for i in range(agent_count):
            soul = dashboard_state['digital_souls'][i]
            comm_system.register_agent(
                f"AGENT-{i+1:03d}",
                soul['digital_soul_hash'],
                f"Agent-{i+1}",
                "NY",
                soul['archetype']
            )
        
        # Connect agents
        for i in range(agent_count - 1):
            comm_system.connect_agents(f"AGENT-{i+1:03d}", f"AGENT-{i+2:03d}")
        
        # Start real-time processor
        comm_system.start_realtime_processor()
        
        # Simulate some communication
        comm_system.layer1.create_public_conversation("AGENT-001", "Task Coordination")
        
        stats = comm_system.get_system_statistics()
        
        dashboard_state['agent_communication'] = {
            'system': comm_system,
            'statistics': stats
        }
        DashboardLogger.log("Agent communication system initialized", "SUCCESS")
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        DashboardLogger.log(f"Error initializing agent communication: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/agent-communication')
def get_agent_communication():
    """Get agent communication status"""
    if dashboard_state['agent_communication'] is None:
        return jsonify({'error': 'Agent communication not initialized'})
    return jsonify(dashboard_state['agent_communication']['statistics'])


@app.route('/api/agent-communication/send-message', methods=['POST'])
def send_agent_message():
    """Send a message between agents"""
    try:
        if dashboard_state['agent_communication'] is None:
            return jsonify({'success': False, 'error': 'Agent communication not initialized'})
        
        comm_system = dashboard_state['agent_communication']['system']
        
        layer = request.json.get('layer', 1)
        sender = request.json.get('sender', 'AGENT-001')
        content = request.json.get('content', {})
        
        if layer == 1:
            from agent_communication_protocol import MessageType
            msg_id = comm_system.send_layer1_message(
                sender, MessageType.PUBLIC_BROADCAST, content
            )
        elif layer == 2:
            from agent_communication_protocol import MessageType
            msg_id = comm_system.send_layer2_message(
                sender, 'AGENT-002', MessageType.PRIVATE_MESSAGE, content, 'PRIVATE-001'
            )
        elif layer == 3:
            signal_type = request.json.get('signal_type', 'motor')
            msg_id = comm_system.send_layer3_signal(
                signal_type, sender, content
            )
        
        DashboardLogger.log(f"Sent {layer} message from {sender}", "INFO")
        
        return jsonify({
            'success': True,
            'message_id': msg_id
        })
    except Exception as e:
        DashboardLogger.log(f"Error sending message: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


# Simulation Endpoints
@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start comprehensive simulation"""
    try:
        DashboardLogger.log("Starting comprehensive ATA simulation...")
        dashboard_state['simulation_running'] = True
        
        # Generate souls
        generator = DigitalSoulGenerator()
        souls = generator.generate_population(50)
        dashboard_state['digital_souls'] = [s.to_dict() for s in souls]
        DashboardLogger.log(f"Generated 50 digital souls")
        
        # Execute robot workflows
        workflow = RobotInternetWorkflow()
        import random
        for i in range(10):
            soul = random.choice(dashboard_state['digital_souls'])
            result = workflow.execute_complete_workflow(
                soul['digital_soul_hash'],
                soul['emotional_resonance'],
                {"location": "Virtual City", "weather": "sunny"},
                soul['archetype']
            )
            dashboard_state['robot_workflows'].append(result)
        DashboardLogger.log(f"Executed 10 robot workflows")
        
        # City analysis - extract SNS posts from workflows
        integrator = VirtualCityIntegrator()
        sns_posts = []
        
        for wf in dashboard_state['robot_workflows']:
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
            dashboard_state['city_analysis'] = analysis
            DashboardLogger.log(f"Completed city analysis. Analyzed {len(sns_posts)} SNS posts.")
        else:
            DashboardLogger.log("No SNS posts generated. Skipping city analysis.", "WARNING")
        
        # Global architecture
        citizens = [{'digital_soul_hash': s['digital_soul_hash'],
                     'memory_narrative': s['memory_anchor']['narrative'],
                     'birth_date': s['birth_date']} for s in dashboard_state['digital_souls']]
        arch = GlobalArchitecture()
        arch.initialize_population(citizens)
        for city in ['NY', 'BJ', 'TK']:
            arch.simulate_city_activity(city, 5)
        dashboard_state['global_architecture'] = arch.get_global_status()
        DashboardLogger.log("Initialized global architecture")
        
        # Agent communication
        comm = AgentCommunicationSystem()
        for i in range(5):
            soul = dashboard_state['digital_souls'][i]
            comm.register_agent(f"AGENT-{i+1:03d}", soul['digital_soul_hash'],
                               f"Agent-{i+1}", "NY", soul['archetype'])
        comm.start_realtime_processor()
        dashboard_state['agent_communication'] = {
            'system': comm,
            'statistics': comm.get_system_statistics()
        }
        DashboardLogger.log("Initialized agent communication")
        
        dashboard_state['simulation_running'] = False
        DashboardLogger.log("Comprehensive simulation completed successfully", "SUCCESS")
        
        return jsonify({'success': True, 'message': 'Simulation completed'})
    except Exception as e:
        dashboard_state['simulation_running'] = False
        DashboardLogger.log(f"Simulation error: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/simulation/reset', methods=['POST'])
def reset_simulation():
    """Reset all dashboard data"""
    dashboard_state['digital_souls'] = []
    dashboard_state['robot_workflows'] = []
    dashboard_state['city_analysis'] = None
    dashboard_state['global_architecture'] = None
    dashboard_state['agent_communication'] = None
    dashboard_state['simulation_running'] = False
    dashboard_state['logs'] = []
    DashboardLogger.log("Dashboard reset", "INFO")
    return jsonify({'success': True})


if __name__ == '__main__':
    DashboardLogger.log("ATA Dashboard starting...")
    app.run(debug=True, host='0.0.0.0', port=5001)
