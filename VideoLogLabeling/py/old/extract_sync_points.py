from py.parsers import BehaviorParser




if __name__ == "__main__":
    log_dir = '../log'

    events = read_logs(log_dir)
    print(events)

    for e in events:
        for g in e.games:
            for l in g.logs.values():
                if not l.has_syncing_file():
                    print e, '/', g, '/', l, '- missing syncing file! creating default ...'
                    l.create_default_syncing_file()
                if not l.has_label_file():
                    print e, '/', g, '/', l, '- missing label file! creating default ...'
