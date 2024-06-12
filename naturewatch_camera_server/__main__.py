from naturewatch_camera_server import create_app, create_error_app
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Launch My Naturewatch Camera')
parser.add_argument('-p', action='store', dest='port', default=5000,
                    help='Port number to attach to')
args = parser.parse_args()

class CameraNotFoundException(Exception):
    pass

def is_camera_enabled():
    camcheck_process = subprocess.Popen(['libcamera-hello', '--list-cameras'], stdout=subprocess.PIPE, text=True)
    grep_process = subprocess.Popen(["grep", "-c", "0 : imx"], stdin=camcheck_process.stdout, stdout=subprocess.PIPE, text=True) 
    output, error = grep_process.communicate()
    return output.strip()

if __name__ == '__main__':
    try:
        app = create_app()
        app.camera_controller.start()
        app.change_detector.start()
    except Exception as e:
        if isinstance(e) and "Camera is not enabled" in str(e):
            # This error message appears even if the camera _is_ enabled, but the camera is not found.
            # e.g. due to a connection problem.
            # We don't want to mislead users into messing with raspi-config, so check if the
            # camera interface is really disabled.
            if (is_camera_enabled()):
                e = CameraNotFoundException("Unable to access camera. Is the cable properly connected?")

        app = create_error_app(e)

    app.run(debug=True, use_reloader=False, use_debugger=True, threaded=True, port=args.port, host='0.0.0.0')
