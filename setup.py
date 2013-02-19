from setuptools import setup, find_packages

version = '1.0dev'

setup(name='experimental.utf8id',
        version=version,
        description='Allow UTF8 in Zope',
        long_description=open('README.rst').read(),
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Plone',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Programming Language :: Python :: 2 :: Only',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        keywords='',
        author='Wichert Akkerman',
        author_email='wichert@simplon.biz',
        license='GPL',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        namespace_packages=[],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'setuptools',
            'Zope2',
            'Products.CMFCore',
            'Products.CMFFormController',
            'Products.CMFPlone',
        ],
        entry_points='''
        [z3c.autoinclude]
        target = plone
        ''',
        )
