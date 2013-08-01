# cnx-user

## Development and Building

Below are instructions for hosting and building the site.

### Hosting Yourself

#### Download and build development version

1. Install [Node.js](http://nodejs.org) (and npm)
2. Run `npm install -g grunt-cli` to install [grunt-cli](https://github.com/gruntjs/grunt-cli)
3. Run `npm install` to install test and build dependencies
4. (optional) Run tests with `npm test`
5. Build the production code with `grunt dist` or `npm run-script dist`
6. Configure your server to point at `dist/index.html`
  * Note: You can also host the development version at `site/index.html` (no build required)
  * Note: Unresolveable URIs should also load `dist/index.html` or `site/index.html`

License
-------

This software is subject to the provisions of the GNU Affero General Public License Version 3.0 (AGPL). See license.txt for details. Copyright (c) 2013 Rice University.