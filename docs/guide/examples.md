---
title: "Perceptual hashing examples in Python: duplicates, search"
description: "Runnable Python examples: find duplicate images, hash distance, SQLite storage, nearest hashes with numpy, BK-tree groups and choosing a threshold."
---

# Examples

The scripts in [`examples/`](https://github.com/gudoshnikovn/python-libphash/tree/main/examples)
run from the repository root on libphash's test images; each one's docstring shows the
command and what it prints, and the test suite runs them all and compares. Four are
twins of [libphash's C examples](https://github.com/gudoshnikovn/libphash/tree/main/examples),
and the tests require both to print the same.

## Find duplicates

```python
--8<-- "examples/find_duplicates.py"
```

## Hash distance between two images

```python
--8<-- "examples/hash_distance.py"
```

## One picture from three sources

```python
--8<-- "examples/load_sources.py"
```

## Every kind of source

```python
--8<-- "examples/sources.py"
```

## Configuration

```python
--8<-- "examples/configure.py"
```

## Storing in SQLite

```python
--8<-- "examples/store_sqlite.py"
```

## Nearest hashes with numpy

```python
--8<-- "examples/nearest_numpy.py"
```

## Groups with a BK-tree

```python
--8<-- "examples/bk_tree.py"
```

## Threads, processes and asyncio

```python
--8<-- "examples/concurrency.py"
```

## Choosing a threshold

libphash's
[Choosing a threshold](https://gudoshnikovn.github.io/libphash/theory/comparing/#choosing-a-threshold)
gives each algorithm's threshold on its corpora; the script measures it on your own
pairs.

```python
--8<-- "examples/threshold.py"
```
