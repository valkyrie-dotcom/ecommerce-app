# Practical Task 2: Research

## 1. The Python 'requestst' module

'requests' is a third-party Python library frequently used when developing
in web frameworks (such as Django or Flask - which is what I mainly use at
work). It allows the Python programme to communicate with web
servers over HTTP. This is achieved by wrapping existing Python tools into
a single readable line or request.

A function is called from Python through requests using one of the
recognised methods (get or post). Post requests will contain the appropriate
data in its body, as per a previous lesson. Examples of these would be
`requests.get(url)` or `requests.post(url, data=...)`. Thereafter, a
'Response' object is received from the server, which will contain:

- the status code (`response.status_code`),
- the headers,
- the raw text (`response.text`) and
- a `.json()` method that converts a JSON body into
Python dictionaries and lists.

Query strings, headers, cookies, form data,
JSON bodies, timeouts and authentication can all be passed as arguments, and
a `Session` object can keep cookies and settings across several requests.

It is frequently used to call APIs, download pages or files, and test web
applications, such as checking that a Django view returns the
expected status code.

## 2. JSON vs XML

### JSON

Used for lightweight data transmission or exchange between web servers, or
lightweight configuration files that store settings for software or tools.
It is also sometimes used as an intermediary between different
programming languages as it is language-agnostic. It is used when
lightweight, fast flexibility is required (lower bandwidth usage).

Advantages:
1. It is short and compact for fast and lightweight transfer
2. Easy to compile and read (human-readable)
3. Simple parsing (maps very neatly onto Python dictionaries, lists, strings)
4. Common format for web APIs, easy to find support

Disadvantages:
1. No comment syntax
2. No native validation/definition/schema of structure
3. Limited data formats (e.g dates stored as string)
4. No attributes or namespaces (could be tricky to consolidate across sources)

### XML

XML, similar to JSON, is used for data transmission or exchange between web
servers, or lightweight configuration files that store settings for software
or tools. It also forms the underlying structure of popular document suites,
such as the MSOffice suite. It is used when more structure and schema
validation is required.

Advantages:
1. Enforceable structure, type in defined schema
2. Can assign attributes and namespaces to elements in complex/mixed data
3. Supports comments and mark-up
4. Mature with many tools and wide adoption in established enterprise systems

Disadvantages:
1. Wordy and heavy message structure
2. Harder to read and compile
3. Parsing into native Python objects requires more work
4. No native support for arrays or numbers, text only

## 3. RESTful APIs

A Representational State Transfer (REST) API is a manner in which programs
can access and use a service via HTTP. The service exposes a URL with
resources. The client then uses the HTTP methods such as GET and POST to
interact with it. For example, a REST API could let a mobile app list
products or place an order using the same data as the website.

Please note that this is different from a webhook, which pushes data
to a client when an event is triggered. A REST API only receives
requests and provides responses.

Advantages:
1. Scalable because requests are stateless (horizontal scaling)
2. Simplicity - Easy to learn, uses ordinary HTTP, URLs and familiar tools
3. Modular (client and server can be amended independently)
4. Works with any programming language and data transfer (e.g JSON vs XML)

Disadvantages:
1. Stateless requests means additional overhead to resend authentication data
(unless cached as responses can declare themselves cacheable)
2. Prone to over-fetching and under-fetching (more or less data than needed)
3. Flexibility means no set standard - requires extensive documentation
4. Requires extensive security as it is exposed to the web
5. Not ideally suited to real-time updates as you require constant refreshes