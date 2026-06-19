from setuptools import find_packages, setup


setup(
    name="patched-flow-demo",
    version="0.8.1",
    description="A strange transformer thing for demo use",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["FastAPI>=0.70", "uvicorn>=0.12", "Flask>=1.0", "requests>=2.6"],
    python_requires=">=2.7",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.9",
    ],
)
