#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.parse
import http.server
import socketserver

# Ensure the parent directory is in the path to import generate_datafile
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_datafile

PORT = 8050

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class SimulationServerHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging every single SSE chunk to prevent console spam
        try:
            message = format % args
            if "api/run" in message and "200 -" in message:
                return
        except Exception:
            pass
        super().log_message(format, *args)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        if path == '/api/run':
            self.handle_api_run(query)
            return
            
        # Serve static files from 'web' directory
        if path == '/' or path == '/index.html':
            self.serve_file('web/index.html', 'text/html')
        elif path == '/style.css':
            self.serve_file('web/style.css', 'text/css')
        elif path == '/app.js':
            self.serve_file('web/app.js', 'application/javascript')
        else:
            self.send_error(404, "File Not Found")

    def serve_file(self, rel_path, content_type):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            self.send_error(404, f"File Not Found: {rel_path}")
            return
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def handle_api_run(self, query):
        # Parse configuration from query string with defaults matching generate_datafile.py
        params = {
            "soulCount": int(query.get("soulCount", [50])[0]),
            "trustWeight": float(query.get("trustWeight", [0.30])[0]),
            "altruismWeight": float(query.get("altruismWeight", [0.25])[0]),
            "ambitionWeight": float(query.get("ambitionWeight", [0.20])[0]),
            "curiosityWeight": float(query.get("curiosityWeight", [0.15])[0]),
            "fearWeight": float(query.get("fearWeight", [0.10])[0]),
            "learningRate": float(query.get("learningRate", [0.01])[0]),
            "explorationRate": float(query.get("explorationRate", [0.30])[0])
        }
        steps_count = int(query.get("steps", [500])[0])
        delay = float(query.get("delay", [0.03])[0]) # Fast default delay for smooth visualization
        
        # Send SSE Headers
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        print(f"Starting real-time simulation stream: steps={steps_count}, delay={delay}s, params={params}")
        
        try:
            for t in range(1, steps_count + 1):
                timestep = f"t{t}"
                
                # 1. Generate souls
                souls = [generate_datafile.generate_soul() for _ in range(params["soulCount"])]
                
                # 2. Run simulation cycle
                sim_res = generate_datafile.run_simulation(souls)
                
                # 3. Evaluate decisions
                decisions = generate_datafile.evaluate_decisions(sim_res["democraticHealth"], params)
                
                # 4. Construct payload
                step_data = {
                    "timestep": timestep,
                    "cycle_id": sim_res["cycleId"],
                    "citizens": sim_res["citizenCount"],
                    "observations": sim_res["observationCount"],
                    "posts": sim_res["postCount"],
                    "overall_index": sim_res["democraticHealth"]["overallIndex"],
                    "collapse_risk": sim_res["democraticHealth"]["collapseRisk"],
                    "social_cohesion": sim_res["democraticHealth"]["socialCohesion"],
                    "economic_health": sim_res["democraticHealth"]["economicHealth"],
                    "participation_rate": sim_res["democraticHealth"]["participationRate"],
                    "trust_weight": params["trustWeight"],
                    "altruism_weight": params["altruismWeight"],
                    "ambition_weight": params["ambitionWeight"],
                    "curiosity_weight": params["curiosityWeight"],
                    "fear_weight": params["fearWeight"],
                    "decisions": decisions,
                    "timestamp": generate_datafile.datetime.now(generate_datafile.timezone.utc).isoformat().replace("+00:00", "Z")
                }
                
                # Write to stream
                self.wfile.write(f"data: {json.dumps(step_data)}\n\n".encode('utf-8'))
                self.wfile.flush()
                
                # 5. Optimize parameters
                params = generate_datafile.optimize_parameters(sim_res["democraticHealth"], params)
                
                time.sleep(delay)
                
        except (ConnectionResetError, BrokenPipeError):
            print("Client disconnected from simulation stream.")
        except Exception as e:
            print(f"Error in simulation stream thread: {e}")

def main():
    print("🧬 Starting ATA Simulation Dashboard Backend...")
    print(f"Address: http://localhost:{PORT}")
    
    server = ThreadingHTTPServer(('0.0.0.0', PORT), SimulationServerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
        print("Server stopped.")

if __name__ == "__main__":
    main()
