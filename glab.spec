#
# Conditional build:
%bcond_without	tests		# unit tests

%define		vendor_version	1.124.0

Summary:	GitLab command line tool
Summary(pl.UTF-8):	Narzędzie wiersza poleceń GitLaba
Name:		glab
Version:	1.124.0
Release:	1
License:	MIT
Group:		Development/Tools
#Source0Download: https://gitlab.com/gitlab-org/cli/-/releases
Source0:	https://gitlab.com/gitlab-org/cli/-/archive/v%{version}/cli-v%{version}.tar.bz2
# Source0-md5:	3db68158d9990fc6d2c793be2bd6fc33
# cd cli-v%{version}
# go mod vendor
# cd ..
# tar cJf glab-vendor-%{version}.tar.xz cli-v%{version}/vendor
Source1:	%{name}-vendor-%{vendor_version}.tar.xz
# Source1-md5:	0889a65b77ef2f53b9becd4f719c61c9
Patch0:		%{name}-telemetry-opt-in.patch
URL:		https://gitlab.com/gitlab-org/cli
BuildRequires:	golang >= 1.27.2
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.009
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%if %{with tests}
BuildRequires:	git-core
%endif
Requires:	git-core
ExclusiveArch:	%go_arches
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%undefine	_debugsource_packages

%description
glab is GitLab on the command line. It brings merge requests, issues,
pipelines and other GitLab concepts to the terminal next to where you
are already working with git and your code.

%description -l pl.UTF-8
glab to narzędzie wiersza poleceń GitLaba. Udostępnia zgłoszenia,
prośby o scalenie, potoki CI/CD i inne elementy GitLaba z poziomu
terminala, w którym pracuje się już z gitem i kodem.

%package -n bash-completion-glab
Summary:	Bash completion for glab command line
Summary(pl.UTF-8):	Dopełnianie linii poleceń glab dla Basha
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-glab
Bash completion for glab command line.

%description -n bash-completion-glab -l pl.UTF-8
Dopełnianie linii poleceń glab dla Basha.

%package -n fish-completion-glab
Summary:	Fish completion for glab command line
Summary(pl.UTF-8):	Dopełnianie linii poleceń glab dla Fisha
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	fish
BuildArch:	noarch

%description -n fish-completion-glab
Fish completion for glab command line.

%description -n fish-completion-glab -l pl.UTF-8
Dopełnianie linii poleceń glab dla Fisha.

%package -n zsh-completion-glab
Summary:	ZSH completion for glab command line
Summary(pl.UTF-8):	Dopełnianie linii poleceń glab dla ZSH
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	zsh
BuildArch:	noarch

%description -n zsh-completion-glab
ZSH completion for glab command line.

%description -n zsh-completion-glab -l pl.UTF-8
Dopełnianie linii poleceń glab dla ZSH.

%prep
%setup -q -a1 -n cli-v%{version}
%patch -P0 -p1

%{__mv} cli-v%{vendor_version}/vendor .

%{__mkdir_p} .go-cache

%build
# upstream release builds and CI use pure Go
export CGO_ENABLED=0

%__go build -v -mod=vendor -trimpath -ldflags "-X main.version=v%{version}" -o target/glab ./cmd/glab

%__go run -mod=vendor ./cmd/gen-docs --manpage --path target/man

%if %{with tests}
# test helpers locate the source root with git rev-parse
git init -q
install -d test-home
# prompt tests script keystrokes into an emulated terminal; the caller's
# SSH_TTY or TERM=dumb changes bubbletea's terminal queries and keys get lost;
# editor, pager and token variables are cleared like upstream's "make test"
# -count=1: fsx tests stat() in a tight loop and the go test result cache
# then spends ages hashing millions of logged file accesses
HOME=$(pwd)/test-home \
env -u SSH_TTY -u TERM -u VISUAL -u EDITOR -u PAGER -u GITLAB_TOKEN \
%__go test -mod=vendor -count=1 ./...
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,%{bash_compdir},%{fish_compdir},%{zsh_compdir}}

install -p target/glab $RPM_BUILD_ROOT%{_bindir}/glab
cp -p target/man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

# glab creates its config directory on every start
export GLAB_CONFIG_DIR=$(pwd)/glab-config
./target/glab completion -s bash > $RPM_BUILD_ROOT%{bash_compdir}/glab
./target/glab completion -s fish > $RPM_BUILD_ROOT%{fish_compdir}/glab.fish
./target/glab completion -s zsh > $RPM_BUILD_ROOT%{zsh_compdir}/_glab

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE README.md
%attr(755,root,root) %{_bindir}/glab
%{_mandir}/man1/glab.1*
%{_mandir}/man1/glab-*.1*

%files -n bash-completion-glab
%defattr(644,root,root,755)
%{bash_compdir}/glab

%files -n fish-completion-glab
%defattr(644,root,root,755)
%{fish_compdir}/glab.fish

%files -n zsh-completion-glab
%defattr(644,root,root,755)
%{zsh_compdir}/_glab
