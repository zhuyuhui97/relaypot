RELAYPOT_HOME=`pwd`
FRMOD='relaypot'
BKMOD='relaypot-backend'
RUN_DIR='/var/run/relaypot'
LOG_DIR='/var/log/relaypot'

init_dirs() {
    if [ ! -d $RUN_DIR ]; then
        sudo mkdir -p $RUN_DIR
        sudo chown pot:pot $RUN_DIR
    fi

    if [ ! -d $LOG_DIR ]; then
        sudo mkdir -p $LOG_DIR
        sudo chown pot:pot $LOG_DIR
    fi
}

start() {
    if [ ! -z $2 ]; then
        CFG_PARAM="-c $2"
    fi
    echo $1 | grep 'backend' >/dev/null 2>/dev/null
    if [ $? -eq 0 ]; then # If $1 contains 'backend', run backend but give a special name for running files.
        PYTHONPATH=$RELAYPOT_HOME/src twistd --pidfile=$RUN_DIR/$1.pid --logfile=$LOG_DIR/$1.log $BKMOD $CFG_PARAM
    else
        PYTHONPATH=$RELAYPOT_HOME/src twistd --pidfile=$RUN_DIR/$1.pid --logfile=$LOG_DIR/$1.log $FRMOD -p $1 $CFG_PARAM
    fi
}

stop() {
    kill $(cat $RUN_DIR/$1.pid)
}

watch() {
    tail -f $LOG_DIR/$1.log
}

$*
