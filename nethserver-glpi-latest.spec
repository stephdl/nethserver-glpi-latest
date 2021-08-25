Name: nethserver-glpi-latest
Version: 1.0.0
Release: 1%{?dist}
Summary: Configure glpi
Source: %{name}-%{version}.tar.gz
BuildArch: noarch
URL: %{url_prefix}/%{name}
License: GPL
%define glpi_version 9.5.5
%define glpi_name glpi
Source1: https://github.com/glpi-project/glpi/releases/download/%{glpi_version}/%{glpi_name}-%{glpi_version}.tgz 
Source2: glpi-local_define.php
Source3: glpi-downstream.php
Source4: glpi-logrotate

BuildRequires: nethserver-devtools

Requires: nethserver-httpd
Conflicts: glpi
Requires: nethserver-rh-php73-php-fpm
Requires: sclo-php73-php-sodium rh-php73-php-xmlrpc libsodium
Requires: nethserver-rh-mariadb105
%description
Install and configure a glpi instance on NethServer
GLPI is the Information Resource-Manager with an additional Administration-
Interface. You can use it to build up a database with an inventory for your 
company (computer, software, printers...). It has enhanced functions to make
the daily life for the administrators easier, like a job-tracking-system with
mail-notification and methods to build a database with basic information 
about your network-topology.

%prep

%setup

%build
%{makedocs}
perl createlinks
mkdir -p root/etc/e-smith/templates/etc/glpi/config_db.php
ln -s /etc/e-smith/templates-default/template-begin-php root/etc/e-smith/templates/etc/glpi/config_db.php/template-begin
sed -i 's/_RELEASE_/%{version}/' %{name}.json

%install
rm -rf %{buildroot}
(cd root   ; find . -depth -print | cpio -dump %{buildroot})

# set specific settings
mkdir -p %{buildroot}/etc/%{glpi_name}
cp  %SOURCE2 %{buildroot}/etc/%{glpi_name}/local_define.php

# configuration file path
mkdir -p %{buildroot}/usr/share/%{glpi_name}/inc
cp  %SOURCE3 %{buildroot}/usr/share/glpi/inc/downstream.php

# Log rotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cp -pr %SOURCE4 %{buildroot}%{_sysconfdir}/logrotate.d/glpi

# move all files to /usr/share/glpi
mkdir -p  %{buildroot}%{_datadir}/%{glpi_name}
tar xzvf %{SOURCE1} -C %{buildroot}/usr/share

# ===== files =====

mkdir -p %{buildroot}/%{_localstatedir}/lib/%{glpi_name}
mv %{buildroot}/usr/share/%{glpi_name}/files/* %{buildroot}/%{_localstatedir}/lib/%{glpi_name}

# ===== log =====
mkdir -p %{buildroot}%{_localstatedir}/log
mv %{buildroot}/%{_localstatedir}/lib/%{glpi_name}/_log %{buildroot}%{_localstatedir}/log/%{glpi_name}


# clean up
find %{buildroot} -name remove.txt -exec rm -f {} \; -print


mkdir -p %{buildroot}/usr/share/cockpit/%{name}/
mkdir -p %{buildroot}/usr/share/cockpit/nethserver/applications/
mkdir -p %{buildroot}/usr/libexec/nethserver/api/%{name}/
cp -a manifest.json %{buildroot}/usr/share/cockpit/%{name}/
cp -a logo.png %{buildroot}/usr/share/cockpit/%{name}/
cp -a %{name}.json %{buildroot}/usr/share/cockpit/nethserver/applications/
cp -a api/* %{buildroot}/usr/libexec/nethserver/api/%{name}/

mkdir -p %{buildroot}/var/opt/rh/rh-mariadb105/lib/mysql-glpi

%{genfilelist} %{buildroot} \
    --dir /var/log/glpi 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_cache 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_cron 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_dumps 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_graphs 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_locales 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_lock 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_pictures 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_plugins 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_rss 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_sessions 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_tmp 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_uploads 'attr(2770,apache,apache)' \
    --dir /var/opt/rh/rh-mariadb105/lib/mysql-glpi 'attr(0755,mysql,mysql)'  | grep -v -e '/usr/share/glpi'\
     > %{name}-%{version}-filelist

%files -f %{name}-%{version}-filelist
%defattr(-,root,root)
%doc COPYING
%dir %{_nseventsdir}/%{name}-update
%attr(0440,root,root) /etc/sudoers.d/50_nsapi_nethserver_glpi
%dir %attr(0755,mysql,mysql) /var/opt/rh/rh-mariadb105/lib/mysql-glpi
%{_datadir}/%{glpi_name}
%config(noreplace) %{_sysconfdir}/logrotate.d/glpi
%dir %attr(2770,apache,apache) %{_sysconfdir}/%{glpi_name}
%config(noreplace) %{_sysconfdir}/%{glpi_name}/local_define.php
%dir %attr(0750,apache,apache) %{_datadir}/%{glpi_name}/config
%dir %attr(0750,apache,apache) %{_datadir}/%{glpi_name}/marketplace
# This folder can contain private information (sessions, docs, ...)
%attr(2770,apache,apache) %{_localstatedir}/lib/%{glpi_name}/*
%attr(2770,apache,apache) %dir %{_localstatedir}/log/%{glpi_name}

%postun
if [ $1 == 0 ] ; then
    /usr/bin/rm -f /etc/httpd/conf.d/glpi.conf
    /usr/bin/systemctl reload httpd
fi

%changelog
* Fri Jul 30 2021 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.3-1
- Fix blank line in config_db.php  
- https://github.com/stephdl/nethserver-glpi/pull/2
- code from mrmarkus

* Sat Jul 04 2020 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.2-1
- Remove http templates after rpm removal

* Thu Mar 05 2020  stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.1-1.ns7
- Fix bad sudoers permission

* Thu Dec 19 2019 Stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.0-1.NS7
- Link in the cockpit application Page

* Sun Sep 10 2017 Stephane de Labrusse <stephdl@de-labrusse.fr> 0.1.4-1.ns7
- Restart httpd service on trusted-network

* Wed Mar 29 2017 Stephane de Labrusse <stephdl@de-labrusse.fr> 0.1.3-1.ns7
- Template expansion on trusted-network

* Mon Mar 20 2017 stephane de Labrusse <stephdl@de-labrusse.fr> 0.1.2-1.ns7
- Redirect the cron job email to /dev/null

* Sun Mar 19 2017 stephane de Labrusse <stephdl@de-labrusse.fr> 0.1.1-1.ns7
- First release to NS7
