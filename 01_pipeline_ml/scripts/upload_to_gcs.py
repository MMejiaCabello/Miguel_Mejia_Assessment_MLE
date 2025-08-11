from google.cloud import storage

def create_bucket_if_not_exists(bucket_name: str, location: str = "US"):
    client = storage.Client()
    bucket = client.lookup_bucket(bucket_name)
    
    if bucket is None:
        print(f"[INFO] Bucket '{bucket_name}' no existe. Creando...")
        bucket = client.create_bucket(bucket_name, location=location)
        print(f"[INFO] Bucket '{bucket_name}' creado.")
    else:
        print(f"[INFO] Bucket '{bucket_name}' ya existe.")
    
    return bucket

def upload_file_to_bucket(bucket_name: str, local_file_path: str, destination_blob_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    print(f"[INFO] Archivo '{local_file_path}' subido a 'gs://{bucket_name}/{destination_blob_name}'.")

if __name__ == "__main__":
    # 👇 Personaliza estos valores antes de ejecutar
    bucket_name = "assessment-mle"
    local_file_path = "data/clientes.csv"
    destination_blob = "datasets/clientes.csv"

    create_bucket_if_not_exists(bucket_name, location="US")
    upload_file_to_bucket(bucket_name, local_file_path, destination_blob)