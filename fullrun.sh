# clear queues
dpsiw qclear
# clear all messages table
dpsiw mt-rm
# produce 1 message
dpsiw produce -n "${1:-1}"
# start worker
dpsiw consume
# Output
dpsiw mt-ls