/**
 * main index file for Music This Week
 * Nick Speal, 2016
 */


var server = require("./server");
var router = require("./router");
var requestHandlers = require("./requestHandlers");
var spotifyHandler = require("./spotifyHandler");

// Define what methods to call for each pathname:
var handle = {};
handle["/"] = requestHandlers.welcome;
handle["/findEvents"] = requestHandlers.findEvents;
handle["/viewEvents"] = requestHandlers.viewEvents;
handle["/login"] = spotifyHandler.login;
handle["/callback"] = spotifyHandler.callback;
handle["/refresh_token"] = spotifyHandler.refresh_token;

server.start(router.route, handle);