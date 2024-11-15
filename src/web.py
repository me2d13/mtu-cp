from adafruit_httpserver import Server, Request, Response, Websocket, GET, MIMETypes
import wifi
from log import log_items, get_last_log, pdebug
from api import JoyApi, MotorApi
import gc

MIMETypes.configure(
    default_to="text/plain",
    # Unregistering unnecessary MIME types can save memory
    keep_for=[".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico"],
)

pages = {
    "/": "Main",
    "/log": "Log",
    "/joy": "Joystick",
    "/motors": "Motors",
    "/about": "About",
}

def webpage(title, content, nav, js = None):
    js_code = "" if js is None else f"<script src=\"{js}\"></script>"
    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <title>{title}</title>
    <link rel="stylesheet" href="main.css" />
</head>

<body>
    {js_code}
    <div id="wrapper">
        <header>
            {title}
        </header>
        <section id="content">
            <nav>
                <ul>
                    {nav}
                </ul>
            </nav>
            <article>
                {content}
            </article>
        </section>
        <footer>
            Footer
        </footer>
    </div>
    <script src="scripts.js"></script>
</body>

</html>
    """
    return html

class WebServer:
    def __init__(self, pool, joystick, motor):
        self.joystick = joystick
        # Create an HTTP server instance
        self.server = Server(pool, "/static", debug=True)
        self.joy_api = JoyApi(joystick, self.server)
        self.motor_api = MotorApi(self.server, motor)
        self.websocket: Websocket = None
        self.current_page = "/"
        self.last_sent_log = None

        # Add a route for the root path
        @self.server.route("/")
        def mainPage(request):
            self.current_page = "/"
            return Response(request, f"{webpage('MTU control', 'Hello', self.build_nav())}", content_type='text/html')

        @self.server.route("/log")
        def logPage(request):
            self.current_page = "/log"
            return Response(request, f"{webpage('Logs', self.render_logs(), self.build_nav(), "log.js")}", content_type='text/html')

        @self.server.route("/joy")
        def joyPage(request):
            self.current_page = "/joy"
            with open("/static/joy.html", "r") as file:
                content = file.read()
            return Response(request, f"{webpage(
                'Joystick', 
                content, 
                self.build_nav(), 
                "joy.js")}", 
              content_type='text/html')
        
        @self.server.route("/motors")
        def joyPage(request):
            self.current_page = "/motors"
            with open("/static/motors.html", "r") as file:
                content = file.read()
            return Response(request, f"{webpage(
                'Motors', 
                content, 
                self.build_nav(), 
                "motors.js")}", 
              content_type='text/html')

        @self.server.route("/about")
        def aboutPage(request):
            self.current_page = "/about"
            return Response(request, f"{webpage('MTU about', 'About', self.build_nav())}", content_type='text/html')

        @self.server.route("/connect-websocket", GET)
        def connect_client(request: Request):
            if self.websocket is not None:
                self.websocket.close()  # Close any existing connection
            self.websocket = Websocket(request)
            return self.websocket

    def render_logs(self):
        def to_log_line(log_item):
            return f"<li>{log_item.to_string()}</li>"
        last_log_elmt = f"<div>Last log: <strong id=\"lastLog\">{get_last_log()}</strong></div>"
        return last_log_elmt + "<ul id=\"logs\">" + "\n".join(map(to_log_line, log_items)) + "</ul>"

    def build_nav(self):
        def to_nav_line(page_key):
            return f"<li>{pages[page_key]}</li>" if (page_key == self.current_page) else f"<li><a href=\"{page_key}\">{pages[page_key]}</a></li>"
        return " ".join(map(to_nav_line, pages.keys()))

    def start(self):
        # Start the server
        self.server.start(str(wifi.radio.ipv4_address), 80)
        print(f"Server running at http://{wifi.radio.ipv4_address}")

    def poll(self):
        # Main loop to handle requests
        try:
            self.server.poll()  # Poll for incoming requests
        except Exception as e:
            pdebug("Error:", e)

    def send_logs_if_needed(self):
        if self.websocket is not None and self.last_sent_log != get_last_log():
            def to_json_item(log_item):
                return f"\"{log_item.log_number}\":\"{log_item.to_string()}\""
            json_logs_element = "{" + ",".join(map(to_json_item, log_items)) + "}"
            data_element = "{\"memory\":"+str(gc.mem_free())+"}"
            self.websocket.send_message("{\"logs\":"+json_logs_element+",\"data\":"+data_element+"}", fail_silently=True)
            self.last_sent_log = get_last_log()