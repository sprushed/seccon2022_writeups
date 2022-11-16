# easylfi

This task consists of two parts: firstly, we need to bypass filtration
of `..` and `%` to get the contents of `/flag.txt`, and secondly we
must somehow get rid of `SECCON` in the output of `curl` before it
reaches `@app.after_request` handler, which filters all responses that
contain that substring.

## Bypassing path-traversal filter

From the [curl manpage](https://curl.se/docs/manpage.html) we can learn
that you can use `{}` and `[]` in URL to fetch multiple pages. We can
abuse this to bypass filter by sending request like this:

```py
import requests as rq

url = 'http://easylfi.seccon.games:3000/.{.}/.{.}/flag.txt'

r = rq.get(url)
print(r.content)
```

## Bypassing `SECCON` filter

Valdation function for simple custom template engine contains logical
error, which leads to vulnerability. We can pass single `{` symbol as
a key for template variable and it will pass validation. That enables
us to change symbol in front of `SECCON` in flag `SECCON{...}` to `}`.
That gives us ability to replace it with template. But we still need
`{` in the beginning of template key for it to pass validation. For
that we can request two files with curl feature from previous part and
with some simple manipulations we receive flag.

---
Full sploit can be found in [exploit.py](./exploit.py)