import glob
import os
import shutil
import subprocess
import sys


def create_changelog():
    """Create a changelog file."""
    try:
        # Ensure the 'gitchangelog' module is available
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'gitchangelog'])

        # Create the changelog file
        with open('CHANGELOG.md', 'w') as changelog_file:
            subprocess.check_call(['gitchangelog'], stdout=changelog_file)
        print("Changelog created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create the changelog: {e}")
        sys.exit(1)


def clean_dist():
    """Clean the dist directory."""
    dist_dir = 'dist'
    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)
        print(f"Cleaned '{dist_dir}' directory.")


def build_package():
    """Build the package."""
    try:
        # Ensure the 'build' module is available
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'build'])

        subprocess.check_call([sys.executable, '-m', 'build'])
        print("Package built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build the package: {e}")
        sys.exit(1)


def upload_package():
    """Upload the package to PyPI."""
    # Expand the wildcard to get a list of distribution files
    dist_files = glob.glob('dist/*')

    if not dist_files:
        print("No distribution files found in the 'dist/' directory. Please build the package first.")
        sys.exit(1)

    try:
        # Ensure the 'twine' module is available
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'twine'])

        subprocess.check_call([sys.executable, '-m', 'twine', 'upload'] + dist_files)
        print("Package uploaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upload the package: {e}")
        sys.exit(1)


def main():
    # Ensure we are in the project root directory (where this script is located)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Create the changelog
    create_changelog()

    # Clean the 'dist/' directory
    clean_dist()

    # Build the package
    build_package()

    # Upload the package
    upload_package()


if __name__ == "__main__":
    main()
