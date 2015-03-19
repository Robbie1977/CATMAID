/* -*- mode: espresso; espresso-indent-level: 2; indent-tabs-mode: nil -*- */
/* vim: set softtabstop=2 shiftwidth=2 tabstop=2 expandtab: */

// Declare the CATMAID namespace
var CATMAID = {};

// Add some basic functionality
(function(CATMAID) {

  "use strict";

  /**
   * Throws an error if the provided object is no string of at least length 1.
   */
  var validateString = function(str, name) {
    if (!str || !str.length || str.length === 0) {
      throw Error("No proper " + name + " provided!");
    }
  };

  /**
   * Set up the front-end environment. Both URLs are stored so that they contain
   * a trailing slash.
   *
   * @param {string} backendURL - The URL pointing to CATMAID's back-end.
   * @param {string} staticURL - The URL pointing to CATMAID's static files.
   */
  CATMAID.configure = function(backendURL, staticURL) {
    validateString(backendURL, "back-end URL");
    validateString(staticURL, "static URL");

    Object.defineProperty(CATMAID, "backendURL", {
      enumerable: false,
      configurable: true,
      writable: false,
      value: backendURL.endsWith("/") ? backendURL : backendURL + "/"
    });

    Object.defineProperty(CATMAID, "staticURL", {
      enumerable: false,
      configurable: true,
      writable: false,
      value: staticURL.endsWith("/") ? staticURL : staticURL + "/"
    });
  };

})(CATMAID);
