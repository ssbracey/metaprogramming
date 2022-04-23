TESTS = {
    "allow_snake": "decorators_test.AllowSnakeTests",
    "count_calls": "decorators_test.CountCallsTests",
    "overload": "decorators_test.OverloadTests",
    "positional_only": "decorators_test.PositionalOnlyTests",
    "record_calls": "decorators_test.RecordCallsTests",
    "alias": "descriptors_test.AliasTests",
    "class_only_method": "descriptors_test.ClassOnlyMethodTests",
    "class_property": "descriptors_test.ClassPropertyTests",
    "computed_property": "descriptors_test.ComputedPropertyTests",
    "is_ok": "initial_test.InitialTests",
    "Hashable": "metaclasses_test.HashableTests",
    "InstanceTracker": "metaclasses_test.InstanceTrackerTests",
    "Mapping": "metaclasses_test.MappingTests",
    "NoMethodCollisions": "metaclasses_test.NoMethodCollisionsTests",
    "SnakeTestCase": "metaclasses_test.SnakeTestCaseTests",
    "UnsubclassableType": "metaclasses_test.UnsubclassableTypeTests"
}

MODULES = {
    "decorators": [
        "allow_snake",
        "count_calls",
        "overload",
        "positional_only",
        "record_calls"
    ],
    "descriptors": [
        "alias",
        "class_only_method",
        "class_property",
        "computed_property"
    ],
    "initial": [
        "is_ok"
    ],
    "metaclasses": [
        "Hashable",
        "InstanceTracker",
        "Mapping",
        "NoMethodCollisions",
        "SnakeTestCase",
        "UnsubclassableType"
    ]
}
