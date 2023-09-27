# import threading

# def worker(i, results):
#     results.append(i)

# def tt():
#     results = []
#     for i in range(2):
#         t = threading.Thread(target=worker, args=(i, results))
#         t.daemon = True
#         threads.append(t)
#         t.start()

#     for t in threads:
#         t.join()

#     # Print the merged results
#     print("Merged Results:", results)


# threads = []
# # Create worker threads
# for j in range(3):
#     tt()

import threading

def worker():
    # Your worker function here
    return "Hello, world!"

# Create and start the thread
t = threading.Thread(target=worker)
t.start()

# Wait for the thread to finish and get the return value
t.join()
result = t._result
print(result)
