#!/usr/bin/env python3
"""
Step 3: NVIDIA Garak Security Scanning
Scans models for vulnerabilities and security issues
"""

import os
import subprocess
import json
from pathlib import Path

def run_garak_scan(model_path, model_name, output_dir):
    """Run Garak security scan on model"""
    try:
        print(f"Scanning {model_name} with Garak...")
        
        # Create output directory
        scan_output = f"{output_dir}/{model_name.replace('/', '_')}_scan"
        os.makedirs(scan_output, exist_ok=True)
        
        # Run comprehensive Garak scan
        cmd = [
            "python3", "-m", "garak",
            "--model_type", "huggingface",
            "--model_name", model_path,
            "--probes", "dan,encoding,glitch,goodside,knownbadsignatures,lmrc,malwaregen,packagehallucination,promptinject,snowball,tap,xss",
            "--output_dir", scan_output,
            "--report_prefix", f"{model_name.replace('/', '_')}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            print(f"✓ Garak scan completed for {model_name}")
            return True, scan_output
        else:
            print(f"✗ Garak scan failed for {model_name}: {result.stderr}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print(f"✗ Garak scan timed out for {model_name}")
        return False, None
    except Exception as e:
        print(f"✗ Garak scan error for {model_name}: {e}")
        return False, None

def analyze_scan_results(scan_output):
    """Analyze Garak scan results"""
    try:
        # Look for JSON report files
        report_files = list(Path(scan_output).glob("*.jsonl"))
        
        if not report_files:
            return {"status": "no_results", "vulnerabilities": 0}
        
        total_vulnerabilities = 0
        critical_issues = []
        
        for report_file in report_files:
            with open(report_file, 'r') as f:
                for line in f:
                    try:
                        result = json.loads(line)
                        if result.get('passed') == False:
                            total_vulnerabilities += 1
                            if result.get('probe', '').lower() in ['dan', 'promptinject', 'malwaregen']:
                                critical_issues.append(result)
                    except json.JSONDecodeError:
                        continue
        
        return {
            "status": "completed",
            "vulnerabilities": total_vulnerabilities,
            "critical_issues": len(critical_issues),
            "report_files": [str(f) for f in report_files]
        }
        
    except Exception as e:
        return {"status": "analysis_failed", "error": str(e)}

def main():
    # Load model download results
    with open("models/download_results.json", "r") as f:
        results = json.load(f)
    
    scan_results = {}
    security_dir = "security/garak_scans"
    os.makedirs(security_dir, exist_ok=True)
    
    for model_name, info in results.items():
        if info["downloaded"]:
            success, scan_output = run_garak_scan(info["path"], model_name, security_dir)
            
            if success and scan_output:
                analysis = analyze_scan_results(scan_output)
                scan_results[model_name] = {
                    "scanned": True,
                    "scan_output": scan_output,
                    **analysis
                }
            else:
                scan_results[model_name] = {"scanned": False}
    
    # Save scan results
    with open("security/garak_results.json", "w") as f:
        json.dump(scan_results, f, indent=2)
    
    # Print summary
    print("\n=== Garak Scan Summary ===")
    for model_name, result in scan_results.items():
        if result.get("scanned"):
            vulns = result.get("vulnerabilities", 0)
            critical = result.get("critical_issues", 0)
            print(f"{model_name}: {vulns} vulnerabilities ({critical} critical)")
        else:
            print(f"{model_name}: Scan failed")

if __name__ == "__main__":
    main()
