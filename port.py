import socket
import threading
import time

def scan_port_threaded(host, port, open_ports):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"Port {port} is OPEN")
            open_ports.append(port)
        s.close()
    except Exception as e:
        # print(f"Error scanning port {port}: {e}") 
        pass # 오류 발생 시 그냥 넘어감

def scan_ports_threaded(host, start_port, end_port, num_threads=100):
    print(f"\nScanning {host} from port {start_port} to {end_port} with {num_threads} threads...")
    open_ports = []
    threads = []

    try:
        ip = socket.gethostbyname(host)
        print(f"Resolved IP: {ip}")
    except socket.gaierror:
        print(f"Hostname could not be resolved: {host}")
        return

    # 스캔할 포트 목록 생성
    ports_to_scan = list(range(start_port, end_port + 1))

    # 스레드 생성 및 실행
    for port in ports_to_scan:
        thread = threading.Thread(target=scan_port_threaded, args=(ip, port, open_ports))
        threads.append(thread)
        thread.start()

        # 동시에 실행되는 스레드 수 제한
        while threading.active_count() > num_threads:
            time.sleep(0.1) 


    for thread in threads:
        thread.join()

    if open_ports:
        print(f"\n--- Open Ports on {host} ---")
        for p in sorted(open_ports): 
            try:
                service_name = socket.getservbyport(p)
                print(f"Port {p} ({service_name})")
            except OSError:
                print(f"Port {p} (Unknown service)")
        print("----------------------------")
    else:
        print(f"\nNo open ports found on {host} in the range {start_port}-{end_port}.")

if __name__ == "__main__":
    target_host = input("Enter target host (e.g., scanme.nmap.org): ")
    try:
        start_port_input = input("Enter start port (e.g., 1): ")
        end_port_input = input("Enter end port (e.g., 1024): ")
        num_threads_input = input("Enter number of threads (e.g., 200, default 100): ")

        start_port = int(start_port_input)
        end_port = int(end_port_input)
        num_threads = int(num_threads_input) if num_threads_input else 100

        if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535 and start_port <= end_port):
            print("Invalid port range.")
        elif not (1 <= num_threads <= 1000): 
            print("Number of threads must be between 1 and 1000.")
        else:
            scan_ports_threaded(target_host, start_port, end_port, num_threads)
    except ValueError:
        print("Invalid input. Please enter valid integers.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
