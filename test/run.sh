#!/bin/bash
I=0
while [ $I -le 20 ]
do
    #./run.py -m GET -u /itemstore/sites/4dd732d5b1f2803b76000000 -e bc8217da7987157dcfc027513982ee91ab42678d >> /tmp/pp_1 &
    echo "./run.py -m GET -u /itemstore/sites/4dd732d5b1f2803b76000000?id=$I >> /tmp/pp_1 &"
    ./run.py -m GET -u /itemstore/sites/4dd732d5b1f2803b76000000?id=$I >> /tmp/pp_1 &
    sleep 0.1
    echo "./run.py -m GET -u /itemstore/sites/?id=$I>> /tmp/pp_1 &"
    ./run.py -m GET -u /itemstore/sites/?id=$I>> /tmp/pp_1 &
    sleep 0.1
    let I=$I+1
done
