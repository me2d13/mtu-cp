from adafruit_httpserver import Route, Request, Response, GET, POST, JSONResponse
from log import pdebug

class JoyApi:
    def __init__(self, joystick, server):
        self.joystick = joystick
        self.server = server

        def joystickCommand(request, command = ""):
            response = "Unsupported command: " + command
            if (command == "demo"):
                pdebug("Setting joystick demo positions")
                self.joystick.demo()
                self.joystick.send()
                response = "Demo positions set"
            return Response(request, response, content_type='text/plain')

        def getJoystick(request):
            data = {
                "x": self.joystick._joy_x,
                "y": self.joystick._joy_y,
                "z": self.joystick._joy_z,
                "rx": self.joystick._joy_r_x,
                "ry": self.joystick._joy_r_y,
                "rz": self.joystick._joy_r_z,
                "buttons": self.joystick._buttons_state,
            }
            return JSONResponse(request, data)

        self.server.add_routes(
            [
                Route(
                    path="/api/joy/<command>",
                    methods=POST,
                    handler=joystickCommand,
                ),
                Route(
                    path="/api/joy",
                    methods=GET,
                    handler=getJoystick,
                ),
            ])