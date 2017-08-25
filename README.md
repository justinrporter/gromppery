# The Gromppery
Its thirst for simulations cannot be slaked.

## Configuration

In gromppery/gromppery/local.py, you can set important local configuration options. An example is provided.

## Basic Use

The provided client/gromppery_client.py is a script that can request work from the gromppery, run it, and return it.

It is invoked like:

```bash
$ python ~/projects/gromppery/client/gromppery_client.py \
    --gromppery http://localhost:43443/api \
    --scratch ~/sim/ \
    --protein lambda-repressor \
    --iterations 2
```

This command will connect to a gromppery running at `localhost:43443`, download a work unit from the project called `lambda-repressor`, run it in a directory like `~/sim/YEAR-MONTH-DAY-HASH`, and return it. Because the `--iterations` flag is 2, it will then repeat this process again. If `--iterations` is not specified, it will run until terminated.
