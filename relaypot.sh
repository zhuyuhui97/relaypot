. relaypot.sh.conf

start() {
    if [ ! -z $2 ]; then
        CFG_PARAM="-c $2"
    fi
    echo $1 | grep $BACKEND_PREFIX >/dev/null 2>/dev/null
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

restart(){
    ./scripts/utils.sh stop $* 
    ./scripts/utils.sh start $*
}

batch_restart(){
    while read line; do
        echo $line
        restart $line
    done<./svc
}

update(){
    git fetch
    if [ -e .git/refs/heads/$LOCAL_TARGET ]; then
        # test current branch here!
        REF_LOCAL=".git/refs/heads/$LOCAL_TARGET"
        REF_REMOTE=".git/refs/remotes/$ORIGIN/$REMOTE_TARGET"
        cat .git/HEAD | grep "refs/heads/$LOCAL_TARGET"
        if [ $? != 0 ]; then
            # Current HEAD is not on local runtime branch, reset!
            echo "Switching to branch $LOCAL_TARGET"
            git checkout $LOCAL_TARGET
        fi
        if [ `cat $REF_LOCAL` != `cat $REF_REMOTE` ]; then
            # TODO test if service really should restart here
            # Local HEAD is outdated
            echo "Got new version! Merging remote branch $ORIGIN/$REMOTE_TARGET"
            git checkout $ORIGIN/$REMOTE_TARGET
            git branch -D $LOCAL_TARGET
            git checkout -b $LOCAL_TARGET $ORIGIN/$REMOTE_TARGET
            # git merge $ORIGIN/$REMOTE_TARGET
            batch_restart
        fi
    else
        # first run
        echo "Creating local runtime branch $LOCAL_TARGET based on $ORIGIN/$REMOTE_TARGET"
        git checkout -b $LOCAL_TARGET $ORIGIN/$REMOTE_TARGET
        batch_restart
    fi
}

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
$*