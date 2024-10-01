$storageAcct = "YOUR_STORAGE_ACCOUNT"
(Get-Content training-images/training_labels.json) -replace '<storageAccount>', $storageAcct | Out-File training-images/training_labels.json