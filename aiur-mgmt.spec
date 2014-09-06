Name: aiur-mgmt
Version: 0.1	
Release: 1%{?dist}
Summary: Aiur Management

Group: Applications/System
License: GPLv3
URL: https://raw.githubusercontent.com/daisaacson/aiur-mgmt/aiur-mgmt
Source0: https://raw.githubusercontent.com/daisaacson/aiur-mgmt/%{name}/%{name}-%{version}.tar.gz

#BuildRequires:	
Requires: python

%description
Aiur Managment - A collection of scripts and commands


%prep
%setup -q


%build


%install
rm -rf $RPM_BUILD_ROOT
install -m 0755 -d $RPM_BUILD_ROOT%{_bindir}
install -pm 0755 patch.sh $RPM_BUILD_ROOT%{_bindir}/ayum
install -pm 0755 b64.py $RPM_BUILD_ROOT%{_bindir}/ab64
install -pm 0755 sslComponent.py $RPM_BUILD_ROOT%{_bindir}/assl


%files
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/*


%changelog
* Fri Sep 5 2014 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.1-1
- Initial build
