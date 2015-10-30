def get_all_method_pairs(number_of_methods):
    mxm = [(x, y) for x in range(number_of_methods) for y in range(number_of_methods)]
    return [pair for pair in mxm if (pair[0] != pair[1])]


def lcom():
    number_of_methods = 22
    all_methods = get_all_method_pairs(number_of_methods)

    methods_with_shared_variables = \
        [
            (0, 1), (0, 2), (0, 3), (1, 3), (2, 3)
        ]

    methods_with_shared_variables += [(x[1], x[0]) for x in methods_with_shared_variables]
    methods_without_shared_variables = set(all_methods) - set(methods_with_shared_variables)
    return len(methods_without_shared_variables) - len(methods_with_shared_variables)


def main():
    print lcom()


if __name__ == '__main__':
    main()