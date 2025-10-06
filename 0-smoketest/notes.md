# Introduction

The `0-smoketest` directory provides a quick way to verify basic Solr operations:

1. Indexing and searching documents in an existing collection.  
2. Creating a new core by copying the `_default` configuration.

## Running the Core Creation Test

1. Ensure your Solr server is up and running.  
2. Make the test script executable:
   ```bash
   chmod +x create-core.sh
    ```
3. Execute the script:
If the core is created successfully, you should see output similar to:

    ```bash
    {
    "responseHeader": {
        "status": 0,
        "QTime": 2127
    },
    "core": "smoke_test_v1"
    ```

This confirms that Solr can create a new core using the default config and respond to requests.

## Running the Smoketest Script

1.Run the smoketest script and follow the prompts:
   ```bash
   poetry run python smoketest.py
   ```
Follow the instructions in the terminal. It may ask how many documents to index, etc.

This script generates and indexes sample documents in your `vector_collection`, then verifies the index and shows sample results.

