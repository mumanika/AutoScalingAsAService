#!/bin/bash

read us sy ni id wa hi si st <<< $(top -b -n 1| awk 'NR==3{for (I=1;I<=NF;I++) if ($I == "%Cpu(s):") {printf "%s %s %s %s %s %s %s %s", $(I+1), $(I+3), $(I+5),$(I+7),$(I+9),$(I+11),$(I+13),$(I+15) };}')
echo $us
