// 

/**
 * Spotify Daemon: A place to house methods for interacting with Spotify
 *
 * This basic node.js script authorizes a user with Spotify and
 * exposes the access token for other programs to grab.
 * 
 * Adapted from the simple authorization tutorial at developer.spotify.com
 * Nick Speal, 2016
 */

var request = require('request'); // "Request" library
var querystring = require('querystring');
var cookieParser = require('cookie-parser');
var url = require('url');

var client_id = '338af3083e4e4069960c77b6978cb7a5'; // Your client id
var client_secret = '9beb594d85ce466a9bf208de1f89aad3'; // Your client secret
var redirect_uri = 'http://localhost:8888/callback'; // Your redirect uri

var ACCESS_TOKEN_GLOBAL = null
var REFRESH_TOKEN_GLOBAL = null



// UTILITIES




/**
 * Generates a random string containing numbers and letters
 * @param  {number} length The length of the string
 * @return {string} The generated string
 */
var generateRandomString = function(length) {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};

var stateKey = 'spotify_auth_state';



// CALLBACKS

function login(res) {
	ACCESS_TOKEN_GLOBAL = null //reset these if the user is newly logging in.
  REFRESH_TOKEN_GLOBAL = null

  var state = generateRandomString(16);
  // res.cookie(stateKey, state);

  // your application requests authorization
  var scope = 'user-read-private user-read-email playlist-modify-private'; 
  
  // redirect the user away from our site and to spotify:
  res.writeHead(301,
  {Location: 'https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    })});
  res.end();
}

function callback(res, req) {
  // After initial response from Spotify with an auth code, request refresh and access tokens

  var code = url.parse(req.url).code;
  console.log("[SpotifyHandler]: Got code: " + code);
  var authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    form: {
      code: code,
      redirect_uri: redirect_uri,
      grant_type: 'authorization_code'
    },
    headers: {
      'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
    },
    json: true
  };
  console.log("[SpotifyHandler]: About to ask for a token");
  //Ask Spotify /api/token for user access token, and then save the response:
  request.post(authOptions, function(error, response, body) {
    if (!error && response.statusCode === 200) {
      console.log("[SpotifyHandler]: Got Token.");
      ACCESS_TOKEN_GLOBAL = body.access_token;
      REFRESH_TOKEN_GLOBAL = body.refresh_token;            
    }
    else {
      console.log("[SpotifyHandler]: Bad response from Spotify");
      // console.log(response)
      res.writeHead(301, {Location: '/#' +querystring.stringify({error: 'invalid_token' })});
      res.end()
    }
  });
}

function refresh_token(res, req) {
  // requesting access token from refresh token
  var refresh_token = req.query.refresh_token;
  var authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
    form: {
      grant_type: 'refresh_token',
      refresh_token: refresh_token
    },
    json: true
  };

  request.post(authOptions, function(error, response, body) {
    if (!error && response.statusCode === 200) {
      var access_token = body.access_token;
      res.send({
        'access_token': access_token
      });
    }
  });


}



exports.login = login;
exports.callback = callback;
exports.refresh_token = refresh_token;