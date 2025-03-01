# seed_coding.py
from app import create_app
from extensions import db
from models import CodingQuestion

app = create_app()

problems = [
    {
        "title": "Two Sum",
        "description": "Given an array of integers 'nums' and an integer 'target', return the indices of the two numbers that add up to target. You may assume that each input would have exactly one solution.",
        "difficulty": "Easy",
        "sample_input": "nums = [2, 7, 11, 15], target = 9",
        "sample_output": "[0, 1]"
    },
    {
        "title": "Add Two Numbers",
        "description": "You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.",
        "difficulty": "Medium",
        "sample_input": "l1 = [2,4,3], l2 = [5,6,4]",
        "sample_output": "[7,0,8]"
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "description": "Given a string 's', find the length of the longest substring without repeating characters.",
        "difficulty": "Medium",
        "sample_input": 's = "abcabcbb"',
        "sample_output": "3"
    },
    {
        "title": "Median of Two Sorted Arrays",
        "description": "Given two sorted arrays 'nums1' and 'nums2' of size m and n respectively, return the median of the two sorted arrays.",
        "difficulty": "Hard",
        "sample_input": "nums1 = [1,3], nums2 = [2]",
        "sample_output": "2.0"
    },
    {
        "title": "Longest Palindromic Substring",
        "description": "Given a string 's', return the longest palindromic substring in 's'.",
        "difficulty": "Medium",
        "sample_input": 's = "babad"',
        "sample_output": '"bab"'
    },
    {
        "title": "Zigzag Conversion",
        "description": "Convert a string 's' to a new string in a zigzag pattern on a given number of rows, then read line by line.",
        "difficulty": "Medium",
        "sample_input": 's = "PAYPALISHIRING", numRows = 3',
        "sample_output": '"PAHNAPLSIIGYIR"'
    },
    {
        "title": "Reverse Integer",
        "description": "Given a signed 32-bit integer 'x', return 'x' with its digits reversed. If reversing 'x' causes the value to go outside the signed 32-bit integer range, then return 0.",
        "difficulty": "Easy",
        "sample_input": "x = 123",
        "sample_output": "321"
    },
    {
        "title": "String to Integer (atoi)",
        "description": "Implement the 'atoi' function which converts a string to an integer, handling whitespaces, optional signs, and overflow.",
        "difficulty": "Medium",
        "sample_input": 's = "42"',
        "sample_output": "42"
    },
    {
        "title": "Palindrome Number",
        "description": "Determine whether an integer is a palindrome. An integer is a palindrome when it reads the same backward as forward.",
        "difficulty": "Easy",
        "sample_input": "x = 121",
        "sample_output": "true"
    },
    {
        "title": "Regular Expression Matching",
        "description": "Implement regular expression matching with support for '.' and '*'.",
        "difficulty": "Hard",
        "sample_input": 's = "aa", p = "a*"',
        "sample_output": "true"
    },
    {
        "title": "Container With Most Water",
        "description": "Given n non-negative integers representing the heights of vertical lines, find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "difficulty": "Medium",
        "sample_input": "height = [1,8,6,2,5,4,8,3,7]",
        "sample_output": "49"
    },
    {
        "title": "Integer to Roman",
        "description": "Convert an integer to a Roman numeral.",
        "difficulty": "Medium",
        "sample_input": "num = 58",
        "sample_output": '"LVIII"'
    },
    {
        "title": "Roman to Integer",
        "description": "Convert a Roman numeral to an integer.",
        "difficulty": "Easy",
        "sample_input": 's = "MCMXCIV"',
        "sample_output": "1994"
    },
    {
        "title": "Longest Common Prefix",
        "description": "Given an array of strings, find the longest common prefix string amongst them.",
        "difficulty": "Easy",
        "sample_input": 'strs = ["flower","flow","flight"]',
        "sample_output": '"fl"'
    },
    {
        "title": "3Sum",
        "description": "Given an integer array 'nums', return all unique triplets [nums[i], nums[j], nums[k]] such that they add up to zero.",
        "difficulty": "Medium",
        "sample_input": 'nums = [-1,0,1,2,-1,-4]',
        "sample_output": '[[-1,-1,2],[-1,0,1]]'
    },
    {
        "title": "3Sum Closest",
        "description": "Given an integer array 'nums' and an integer 'target', return the sum of three integers that is closest to target.",
        "difficulty": "Medium",
        "sample_input": 'nums = [-1,2,1,-4], target = 1',
        "sample_output": "2"
    },
    {
        "title": "Letter Combinations of a Phone Number",
        "description": "Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent.",
        "difficulty": "Medium",
        "sample_input": 'digits = "23"',
        "sample_output": '["ad","ae","af","bd","be","bf","cd","ce","cf"]'
    },
    {
        "title": "Generate Parentheses",
        "description": "Given n pairs of parentheses, generate all combinations of well-formed parentheses.",
        "difficulty": "Medium",
        "sample_input": "n = 3",
        "sample_output": '["((()))","(()())","(())()","()(())","()()()"]'
    },
    {
        "title": "Merge Two Sorted Lists",
        "description": "Merge two sorted linked lists and return it as a new sorted list.",
        "difficulty": "Easy",
        "sample_input": "l1 = [1,2,4], l2 = [1,3,4]",
        "sample_output": "[1,1,2,3,4,4]"
    },
    {
        "title": "Merge Intervals",
        "description": "Given an array of intervals, merge all overlapping intervals.",
        "difficulty": "Medium",
        "sample_input": 'intervals = [[1,3],[2,6],[8,10],[15,18]]',
        "sample_output": '[[1,6],[8,10],[15,18]]'
    },
    {
        "title": "Insert Interval",
        "description": "Given a set of non-overlapping intervals, insert a new interval and merge if necessary.",
        "difficulty": "Medium",
        "sample_input": 'intervals = [[1,3],[6,9]], newInterval = [2,5]',
        "sample_output": '[[1,5],[6,9]]'
    },
    {
        "title": "Spiral Matrix",
        "description": "Given an m x n matrix, return all elements of the matrix in spiral order.",
        "difficulty": "Medium",
        "sample_input": 'matrix = [[1,2,3],[4,5,6],[7,8,9]]',
        "sample_output": "[1,2,3,6,9,8,7,4,5]"
    },
    {
        "title": "Jump Game",
        "description": "Given an array of non-negative integers, determine if you can reach the last index.",
        "difficulty": "Medium",
        "sample_input": "nums = [2,3,1,1,4]",
        "sample_output": "true"
    },
    {
        "title": "Jump Game II",
        "description": "Given an array of non-negative integers, return the minimum number of jumps required to reach the last index.",
        "difficulty": "Hard",
        "sample_input": "nums = [2,3,1,1,4]",
        "sample_output": "2"
    },
    {
        "title": "Unique Paths",
        "description": "Given a grid of m x n, return the number of possible unique paths from the top-left to the bottom-right corner.",
        "difficulty": "Medium",
        "sample_input": "m = 3, n = 7",
        "sample_output": "28"
    },
    {
        "title": "Minimum Path Sum",
        "description": "Given a grid filled with non-negative numbers, find a path from top left to bottom right which minimizes the sum of all numbers along its path.",
        "difficulty": "Medium",
        "sample_input": 'grid = [[1,3,1],[1,5,1],[4,2,1]]',
        "sample_output": "7"
    },
    {
        "title": "Word Break",
        "description": "Given a string 's' and a dictionary of strings 'wordDict', return true if s can be segmented into a space-separated sequence of one or more dictionary words.",
        "difficulty": "Medium",
        "sample_input": 's = "leetcode", wordDict = ["leet","code"]',
        "sample_output": "true"
    },
    {
        "title": "Coin Change",
        "description": "Given coins of different denominations and a total amount of money, find the fewest number of coins that you need to make up that amount.",
        "difficulty": "Medium",
        "sample_input": "coins = [1,2,5], amount = 11",
        "sample_output": "3"
    },
    {
        "title": "Longest Increasing Subsequence",
        "description": "Given an integer array, return the length of the longest strictly increasing subsequence.",
        "difficulty": "Medium",
        "sample_input": "nums = [10,9,2,5,3,7,101,18]",
        "sample_output": "4"
    },
    {
        "title": "Decode Ways",
        "description": "A message containing letters is encoded to numbers. Given a non-empty string containing only digits, determine the total number of ways to decode it.",
        "difficulty": "Medium",
        "sample_input": 's = "12"',
        "sample_output": "2"
    }
]

with app.app_context():
    db.create_all()
    for problem in problems:
        new_problem = CodingQuestion(
            title=problem["title"],
            description=problem["description"],
            difficulty=problem["difficulty"],
            sample_input=problem["sample_input"],
            sample_output=problem["sample_output"]
        )
        db.session.add(new_problem)
    db.session.commit()
    print("Coding problems seeded successfully!")
