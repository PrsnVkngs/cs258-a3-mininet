#!/bin/bash
# ---- exp2_commands.sh ----
echo "# BEFORE flows" > result2.txt

sudo ovs-ofctl -O OpenFlow13 show s1 >> result2.txt
sudo ovs-ofctl -O OpenFlow13 dump-flows s1 >> result2.txt

# Run initial pings (expected fail, since no setup done yet)
sudo mnexec -a $(pgrep -f "mininet:h1") ping -c 1 10.0.0.3 >> result2.txt
sudo mnexec -a $(pgrep -f "mininet:h2") ping -c 1 10.0.0.3 >> result2.txt

echo "# Adding flows..." >> result2.txt

# Drop all traffic arriving on port 2 (s1-eth2)
sudo ovs-ofctl -O OpenFlow13 add-flow s1 "priority=100,in_port=2,actions=drop"

# Forward traffic h1→h3 (in port 1 out 3)
sudo ovs-ofctl -O OpenFlow13 add-flow s1 "priority=100,in_port=1,actions=output:3"

# Forward traffic h3→h1 (in port 3 out 1)
sudo ovs-ofctl -O OpenFlow13 add-flow s1 "priority=100,in_port=3,actions=output:1"

# Make s2 behave as a normal switch
sudo ovs-ofctl -O OpenFlow13 add-flow s2 "actions=normal"

# Show final flow tables
sudo ovs-ofctl -O OpenFlow13 dump-flows s1 >> result2.txt
sudo ovs-ofctl -O OpenFlow13 dump-flows s2 >> result2.txt

echo "# AFTER flows" >> result2.txt

# Test again
sudo mnexec -a $(pgrep -f "mininet:h1") ping -c 1 10.0.0.3 >> result2.txt
sudo mnexec -a $(pgrep -f "mininet:h2") ping -c 1 10.0.0.3 >> result2.txt

echo "All done! Results saved in result2.txt"
