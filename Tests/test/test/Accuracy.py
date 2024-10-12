import numpy as np

def calculate_accuracy(arrays, ground_truth):
    # Join the arrays
    combined_array = np.concatenate(arrays)
    
    # Ensure ground_truth is a numpy array
    ground_truth = np.array(ground_truth)
    
    # Initialize list to store accuracies
    accuracies = []
    
    for item in combined_array:
        if item != 0:
            if ground_truth.size == 1:
                # Single ground truth value
                accuracy = (1 - abs(item - ground_truth) / ground_truth)*100
            else:
                # Multiple ground truth values, find the closest
                closest_truth = min(ground_truth, key=lambda x: abs(x - item))
                accuracy = (1 - abs(item - closest_truth) / closest_truth)*100
            
            accuracies.append(accuracy)
    
    # Convert accuracies to numpy array
    accuracies = np.array(accuracies)
    
    # Calculate average accuracy and standard deviation
    avg_accuracy = np.mean(accuracies)
    std_accuracy = np.std(accuracies)
    
    return avg_accuracy, std_accuracy

# Example usage
a1 =[1364, 1364, 1363, 1364, 1364, 1364, 1361, 1363, 1362, 1364, 1364, 1364, 1364, 1361, 1363, 1362, 1363, 1364, 1364, 1363, 1361, 1363, 1364, 1363, 1364, 1364, 1363, 1363, 1364, 1364, 1363, 1364]       
a2 =[1362, 1363, 1361, 1362, 1363, 1363, 1363, 1361, 1364, 1362, 1363, 1364, 1363, 1363, 1364, 1364, 1363, 1363, 1364, 1362, 1363, 1364, 1364, 1363, 1361, 1364, 1362, 1364, 1364, 1361, 1362, 1364]       
a3 =[1361, 1362, 1363, 1361, 1364, 1362, 1364, 1363, 1363, 1361, 1364, 1364, 1362, 1364, 1363, 1363, 1365, 1364, 1364, 1362, 1364, 1363, 1364, 1365, 1361, 1364, 1362, 1363, 1364, 1361, 1362, 1364]   


# Single ground truth
ground_truth_single =1364

# Multiple ground truths
# ground_truth_multiple = [1364,5454]
# ground_truth_multiple = [134,166,205,253,312,385,476,587,725,895,1105,1364]


# Calculate accuracy with single ground truth
avg_acc_single, std_acc_single = calculate_accuracy([a1, a2, a3], ground_truth_single)
print(f"Single ground truth - Average accuracy: {avg_acc_single:.4f}, Standard deviation: {std_acc_single:.4f}")

# # Calculate accuracy with multiple ground truths
# avg_acc_multiple, std_acc_multiple = calculate_accuracy([a1, a2, a3], ground_truth_multiple)
# print(f"Multiple ground truths - Average accuracy: {avg_acc_multiple:.4f}, Standard deviation: {std_acc_multiple:.4f}")