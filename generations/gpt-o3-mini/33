from pathlib import Path
import shutil

target_folder = 'F:/Maverick/desktop/Windows/temp/'

def get_content_delivery_path():
    """
    Get the path of Windows Content Delivery
    """
    path = Path('C:/Users/admin/AppData/Local/Packages/')
    matched = path.glob('*Microsoft.Windows.ContentDeliveryManager*')
    if result := next(matched):
        suffix = 'LocalState/Assets/'
        return result / suffix
    else:
        raise Exception('ContentDeliveryManager Not Found')
    

def jpeg(source_folder, target_folder):
    """
    Copy files from source folder to target folder and add .jpeg suffix
    """
    source = Path(source_folder)
    target = Path(target_folder)
    target.mkdir(parents=True, exist_ok=True)
    
    for file in source.iterdir():
        if file.is_file():
            # Create a new file name by appending .jpeg
            new_name = file.name + ".jpeg"
            target_file = target / new_name
            shutil.copy2(file, target_file)
            print(f"Copied {file.name} to {target_file}")

if __name__ == '__main__':
    source_folder = get_content_delivery_path()
    print(f"Windows Content Delivery path: {source_folder}")
    jpeg(source_folder, target_folder)
