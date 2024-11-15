from adafruit_httpserver import Route, Request, Response, GET, POST, JSONResponse
from log import pdebug

class MotorApi:
    def __init__(self, server, motor):
        self.motor = motor
        self.server = server

        def init_motor(request, index):
            message = self.motor.init()
            return Response(request, message, content_type='text/plain')

        def config(request, index):
            steps = request.query_params.get("steps") or 1
            current = request.query_params.get("current") or 1
            self.motor.set_current(current, current)
            self.motor.set_microsteps(steps)
            return Response(request, "OK", content_type='text/plain')

        def get_data(request, index):
            return JSONResponse(request, self.motor.collect_data())

        def move_motor(request, index, steps, rpm):
            message = self.motor.move(int(steps), int(rpm))
            return Response(request, message, content_type='text/plain')

        def run_motor(request, index, speed):
            message = self.motor.run_with_speed(int(speed))
            return Response(request, message, content_type='text/plain')

        def hold_motor(request, index, val):
            message = self.motor.hold(val)
            return Response(request, message, content_type='text/plain')

        self.server.add_routes(
            [
                Route(
                    path="/api/motor/<index>/init",
                    methods=POST,
                    handler=init_motor,
                ),
                Route(
                    path="/api/motor/<index>/move/<steps>/<rpm>",
                    methods=POST,
                    handler=move_motor,
                ),
                Route(
                    path="/api/motor/<index>/hold/<val>",
                    methods=POST,
                    handler=hold_motor,
                ),
                Route(
                    path="/api/motor/<index>/run/<speed>",
                    methods=POST,
                    handler=run_motor,
                ),
                Route(
                    path="/api/motor/<index>/config",
                    methods=POST,
                    handler=config,
                ),
            ])