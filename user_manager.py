#!/usr/bin/python3
# coding: utf-8
import argparse
from enum import Enum
import getpass

from pymongo import MongoClient
import bcrypt

from cyberapi.authorization import PERMISSIONS


class Color(Enum):
    RED = '\033[31m'
    GRN = '\033[32m'
    RST = '\033[0m'


def parse_args():
    """Arguments parsing."""
    parser = argparse.ArgumentParser(description='Automatic user edition')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--add',
                       action='store_true',
                       help='Add user')
    group.add_argument('--update',
                       action='store_true',
                       help='Update user')
    group.add_argument('--remove',
                       action='store_true',
                       help='Remove user')
    group.add_argument('--list',
                       action='store_true',
                       help='List all users')
    group.add_argument('--list-perms',
                       action='store_true',
                       help='List all permissions')

    parser.add_argument('-v',
                        '--verbose',
                        help='Verbose mode',
                        action='count',
                        default=0
                        )

    parser.add_argument('--mongo-host',
                        type=str,
                        default='localhost',
                        help='Mongo host, default: localhost',
                        )

    parser.add_argument('--mongo-port',
                        type=int,
                        default=27017,
                        help='Mongo port, default: 27017',
                        )

    parser.add_argument('-p',
                        '--perms',
                        action='append',
                        default=[],
                        help='Permissions',
                        )

    parser.add_argument('-n',
                        '--name',
                        type=str,
                        help='User name',
                        )

    args = parser.parse_args()

    return args


def permExist(perm):
    namespace, name = perm.split(':')
    if namespace in PERMISSIONS:
        if name in PERMISSIONS[namespace] or name == '*':
            return True
    return False


if __name__ == '__main__':

    parser = parse_args()

    print(parser)

    mongo = MongoClient(parser.mongo_host, parser.mongo_port)
    db = mongo.planning.users_cyber

    if parser.list:
        cursor = db.find()
        print('[*] Users:')
        for user in cursor:
            print(' - % 10s, %s, [%s]' % (user['username'],
                                          user['hash'], ', '.join(user['permissions'])))
    elif parser.list_perms:
        print('[*] Available permission:')
        for k, v in PERMISSIONS.items():
            print(' - %s:*' % k)
            for p in v:
                print(' - %s:%s' % (k, p))

    else:
        if not parser.name:
            raise Exception('No name')

        perms = [i for i in parser.perms if permExist(i)]

        if parser.add:
            # Check user not exist
            if db.find({'username': parser.name}).count() != 0:
                raise Exception('User already exist')

            # ask password
            passwd = getpass.getpass('Password: ')

            hashPass = bcrypt.hashpw(
                passwd.encode(), bcrypt.gensalt()).decode()

            print('[!] Hash: %s' % hashPass)

            db.insert({
                'username': parser.name,
                'hash': hashPass,
                'permissions': perms,
            })

        elif parser.remove:
            confirm = input('Remove %s [y/N]: ' % parser.name).lower()
            if confirm == 'y':
                ret = db.remove({'username': parser.name}, {'justOne': True})

                print(ret)

        elif parser.update:
            raise NotImplementedError()
