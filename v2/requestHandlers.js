var querystring = require("querystring"),
    fs = require("fs"),
    pythonShell = require('python-shell');

function start(response) {
  // Displays a welcome page

  console.log("[Request handler]: 'start' was called.");

  var content = fs.readFileSync('./welcome.html');

  response.writeHead(200, {"Content-Type": "text/html"});
  response.write(content);
  response.end();
}

function findEvents(response) {
  // Search external databases for upcoming events.
  // Calls eventFinder.py, which queries Eventful (for now) and saves a list of events to a file.

  console.log("[Request handler]: 'findEvents' was called.");

  pythonShell.run('./eventFinder.py', function(err){
    if (err) throw err;
    console.log("Finished running eventFinder.py")

    response.writeHead(200, {"Content-Type": "text/html"});
    response.write("Found upcoming events from Eventful.</br>");
    response.write("<a href='./viewEvents' target='_blank'>View Events</a> or <a href='./login'>Generate Playlist</a>");  
    response.end();
  });
}


function viewEvents(response) {
  // Read the file with a list of events and render it to the browser
  console.log("[Request handler]: 'viewEvents' was called.");

  var content = fs.readFileSync('./tmp/events.json');

  response.writeHead(200, {"Content-Type": "text/json"});
  response.write(content);
  response.end();
}


function login(response) {
  // Authenticate with Spotify, then automatically create the playlist.
  console.log("[Request handler]: 'login' was called.");
  response.writeHead(200, {"Content-Type": "text/html"});
  response.write("Spotify Login goes here.");
  response.end();
}

exports.start = start;
exports.findEvents = findEvents;
exports.viewEvents = viewEvents;
exports.login = login;
