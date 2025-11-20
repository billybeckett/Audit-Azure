#!/usr/bin/env python3
"""
Terraform Destroy Helper
Safe destruction of Terraform-managed Azure resources with confirmation.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False


def check_terraform_files():
    """Check if required Terraform files exist"""
    if not os.path.exists('main.tf'):
        print("❌ Error: main.tf not found in current directory")
        print("   Please run this script from the terraform directory")
        return False

    if not os.path.exists('terraform.tfvars'):
        print("⚠️  Warning: terraform.tfvars not found")
        print("   Make sure you're in the correct directory")
        response = input("Continue anyway? (yes/no): ").strip().lower()
        if response != 'yes':
            return False

    return True


def show_plan():
    """Show what will be destroyed"""
    print("\n" + "=" * 80)
    print("SHOWING DESTRUCTION PLAN")
    print("=" * 80)

    result = subprocess.run(
        "terraform plan -destroy",
        shell=True,
        text=True
    )

    return result.returncode == 0


def confirm_destroy():
    """Get user confirmation for destruction"""
    print("\n" + "=" * 80)
    print("⚠️  DESTROY CONFIRMATION")
    print("=" * 80)
    print("\n⚠️  WARNING: This will permanently delete the following resources:")
    print("   - Virtual Network")
    print("   - All Subnets")
    print("   - Resource Group (if empty)")
    print("\n   This action CANNOT be undone!")
    print()

    # First confirmation
    response1 = input("Are you sure you want to destroy these resources? (yes/no): ").strip().lower()
    if response1 != 'yes':
        print("\n✅ Destruction cancelled. Resources are safe.")
        return False

    # Second confirmation with resource name
    print()
    response2 = input("Type 'DESTROY' in capital letters to confirm: ").strip()
    if response2 != 'DESTROY':
        print("\n✅ Destruction cancelled. Resources are safe.")
        return False

    return True


def destroy_resources():
    """Execute terraform destroy"""
    print("\n" + "=" * 80)
    print("DESTROYING RESOURCES")
    print("=" * 80)

    result = subprocess.run(
        "terraform destroy -auto-approve",
        shell=True,
        text=True
    )

    return result.returncode == 0


def cleanup_state():
    """Optionally clean up Terraform state files"""
    print("\n" + "=" * 80)
    print("CLEANUP OPTIONS")
    print("=" * 80)
    print("\nDo you want to remove Terraform state files?")
    print("⚠️  Only do this if you're completely done with this configuration")
    print()

    response = input("Remove state files? (yes/no): ").strip().lower()
    if response == 'yes':
        files_to_remove = [
            'terraform.tfstate',
            'terraform.tfstate.backup',
            '.terraform.lock.hcl'
        ]

        for file in files_to_remove:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"   ✓ Removed {file}")
                except Exception as e:
                    print(f"   ⚠️  Could not remove {file}: {e}")

        # Remove .terraform directory
        if os.path.exists('.terraform'):
            response2 = input("\nRemove .terraform directory? (yes/no): ").strip().lower()
            if response2 == 'yes':
                import shutil
                try:
                    shutil.rmtree('.terraform')
                    print("   ✓ Removed .terraform directory")
                except Exception as e:
                    print(f"   ⚠️  Could not remove .terraform directory: {e}")


def main():
    """Main function"""
    print("=" * 80)
    print("🗑️  Terraform Destroy Helper")
    print("=" * 80)

    # Check if we're in the right directory
    if not check_terraform_files():
        sys.exit(1)

    # Check if Terraform is initialized
    if not os.path.exists('.terraform'):
        print("\n⚠️  Terraform not initialized.")
        print("   Nothing to destroy.")
        sys.exit(0)

    # Show what will be destroyed
    if not show_plan():
        print("\n❌ Error showing plan. Aborting.")
        sys.exit(1)

    # Get confirmation
    if not confirm_destroy():
        sys.exit(0)

    # Destroy resources
    if destroy_resources():
        print("\n" + "=" * 80)
        print("✅ RESOURCES DESTROYED SUCCESSFULLY")
        print("=" * 80)

        # Offer cleanup
        cleanup_state()

        print("\n" + "=" * 80)
        print("✅ Destruction complete!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ DESTRUCTION FAILED")
        print("=" * 80)
        print("\nSome resources may still exist. Please check the Azure portal.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Destruction cancelled by user. Resources are safe.")
        sys.exit(0)
