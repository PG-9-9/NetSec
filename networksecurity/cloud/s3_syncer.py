import os 

class S3Sync:
    """
    A class for synchronizing local folders with AWS S3 buckets.
    """
    def sync_folder_to_s3(self,folder,aws_bucket_url):
        """
        Syncs a local folder to an AWS S3 bucket.

        Parameters
        ----------
        folder : str
            The local directory path to sync.
        aws_bucket_url : str
            The URL of the AWS S3 bucket where the folder will be synced.

        Executes the 'aws s3 sync' command to synchronize the folder to the S3 bucket.
        """
        command=f"aws s3 sync {folder} {aws_bucket_url}"
        os.system(command)
    
    def sync_folder_from_s3(self,folder,aws_bucket_url):
        """
        Syncs a local folder from an AWS S3 bucket.

        Parameters
        ----------
        folder : str
            The local directory path to store the data.
        aws_bucket_url : str
            The URL of the AWS S3 bucket from which the folder will be synced.

        Executes the 'aws s3 sync' command to synchronize the folder from the S3 bucket.
        """
        command=f"aws s3 sync {aws_bucket_url} {folder}"
        os.system(command)