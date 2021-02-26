# Samepack

A javascript bundler that tries to keep the output bundle similar to the source code.

## Setup

```bash
pip install samepack -U
```

## Usage

```bash
same -o bundle.js tests/sample/index.js
```

See ``tests/sample/index.js`` for an example of how js code is to be written.

## Other

* This cannot pull packages from npm yet.
* This should not be used for serious web apps, it should be used for extensions (to boost review times) and education only.
