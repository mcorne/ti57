# code = """
# def foo()
#     return 111
# x = foo()
# """
# try:
#     exec(code)
#     print(x)
# except Exception as e:
#     print(repr(e))

# from goto import with_goto
# @with_goto
# def range(start, stop):
#     i = start
#     result = []

#     label.begin
#     if i == stop:
#         goto.end

#     result.append(i)
#     i += 1
#     goto.begin

#     label.end
#     return result

# a = range(1, 10)
# print(a)
