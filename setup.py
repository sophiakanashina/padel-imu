from setuptools import setup, find_packages

setup(
    name="padel-imu",
    version="0.1.0",
    description="IMU-based movement analysis for padel players",
    author="Sophia and Sandu",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.11",
)