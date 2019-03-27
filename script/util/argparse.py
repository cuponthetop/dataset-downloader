import argparse


# additional_arg : Dict[str, Dict[str, any]]
# eg) { 'learning_rate': {
#          'name': ['--lr', '-lr'],
#          'dest': 'learning_rate',
#          'help': '',
#          'type': float,
#          'default': 0.0001
#        },
#       'b1': {},
#     }
#
def parse(additional_arg):
    parser = argparse.ArgumentParser()

    # parser.add_argument('--', dest='', help='', default=)

    for k, v in additional_arg.items():
        name = v['name']
        del v['name']
        v['dest'] = k
        parser.add_argument(name, **v)

    return vars(parser.parse_args())
