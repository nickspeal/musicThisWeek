/**
 * main index file for Music This Week
 * Nick Speal, 2016
 */


var server = require("./server");
var router = require("./router");
var requestHandlers = require("./requestHandlers");

// Define what methods to call for each pathname:
var handle = {};
handle["/"] = requestHandlers.start;
handle["/findEvents"] = requestHandlers.findEvents;
handle["/viewEvents"] = requestHandlers.viewEvents;
handle["/login"] = requestHandlers.login;

server.start(router.route, handle);