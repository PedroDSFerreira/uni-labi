import cherrypy
import psutil


class Node(object):
    @cherrypy.expose
    def index(self):
        return "Eu sou o índice do Node (Node.index)"

    @cherrypy.expose
    def page(self):
        return "Eu sou um método do Node (Node.page)"
    @cherrypy.expose
    def cpu(self):
        return "This PC is using "+str(psutil.cpu_percent())+"% of CPU."


class Root(object):
    def __init__(self):
        self.node = Node()

    @cherrypy.expose
    def index(self):
        return "Eu sou o índice do Root (Root.index)"

    @cherrypy.expose
    def page(self):
        return "Eu sou um método do Root (Root.page)"
if __name__ == "__main__":
    cherrypy.quickstart(Root(), "/")
