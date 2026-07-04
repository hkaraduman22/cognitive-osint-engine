unit uMain;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, REST.Types, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS,
  FireDAC.Phys.Intf, FireDAC.DApt.Intf, Data.DB, FireDAC.Comp.DataSet,
  FireDAC.Comp.Client, REST.Response.Adapter, REST.Client, Data.Bind.Components,
  Data.Bind.ObjectScope, Vcl.Grids, Vcl.DBGrids, Vcl.StdCtrls,
  System.Threading; // 2. Gün eklentisi: Asenkron işlemler (TTask) için zorunlu kütüphane

type
  TfrmMain = class(TForm)
    // 1. Gün Bileşenleri
    edtSehir: TEdit;
    cmbSektor: TComboBox;
    btnAra: TButton;
    dbgSonuclar: TDBGrid;
    RestClient: TRESTClient;
    RestRequest: TRESTRequest;
    RestResponse: TRESTResponse;
    RestAdapter: TRESTResponseDataSetAdapter;
    MemTableSonuclar: TFDMemTable;
    dsSonuclar: TDataSource;

    // 2. Gün Eklenen Bileşenler
    btnTaramaBaslat: TButton;
    RestRequestPOST: TRESTRequest;
    RestResponsePOST: TRESTResponse;

    procedure FormCreate(Sender: TObject);
    procedure btnAraClick(Sender: TObject);
    procedure btnTaramaBaslatClick(Sender: TObject); // 2. Gün eklentisi
  private
    procedure APIyeBaglanVeAra(ASehir, ASektor: string);
  public
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

procedure TfrmMain.FormCreate(Sender: TObject);
begin
  edtSehir.TextHint := 'Şehir Giriniz (Örn: Ankara)';
  cmbSektor.Text := 'Sektör Seçiniz';
end;

// --- 1. GÜN: VERİLERİ GETİR (GET) ---
procedure TfrmMain.btnAraClick(Sender: TObject);
begin
  APIyeBaglanVeAra(edtSehir.Text, cmbSektor.Text);
end;

procedure TfrmMain.APIyeBaglanVeAra(ASehir, ASektor: string);
begin
  RestRequest.Params.Clear;
  RestRequest.Method := rmGET;
  RestRequest.Resource := 'companies';

  if ASehir <> '' then
    RestRequest.AddParameter('sehir', ASehir, pkGETrsUnsaved);

  if (ASektor <> '') and (ASektor <> 'Sektör Seçiniz') then
    RestRequest.AddParameter('sektor', ASektor, pkGETrsUnsaved);

  try
    RestRequest.Execute;
    if RestResponse.StatusCode = 200 then
      MemTableSonuclar.Open
    else
      ShowMessage('API''den veri alınamadı. Hata Kodu: ' + IntToStr(RestResponse.StatusCode));
  except
    on E: Exception do
      ShowMessage('Core API henüz ayakta değil veya ulaşılamıyor: ' + E.Message);
  end;
end;

// --- 2. GÜN: OSINT BOTUNU TETİKLE (ASENKRON POST) ---
procedure TfrmMain.btnTaramaBaslatClick(Sender: TObject);
begin
  // Kullanıcıya bilgi veriyoruz (Arayüz kilitlenmeden işlemi arka plana atacağız)
  ShowMessage('OSINT Taraması başlatılıyor. İşlem arka planda devam edecek...');

  // Kullanıcı art arda basmasın diye butonu pasif yapıyoruz
  btnTaramaBaslat.Enabled := False;

  // İşlemi Ana Thread'den (UI) ayırıp arka plana (Task) gönderiyoruz
  TTask.Run(procedure
  begin
    RestRequestPOST.Method := rmPOST;
    RestRequestPOST.Resource := 'companies/scan'; // FastAPI'deki taramayı başlatan endpoint

    try
      RestRequestPOST.Execute;

      // Arka plan işleminden arayüze (UI) güvenli bir şekilde geri dönmek için TThread.Queue kullanıyoruz
      TThread.Queue(nil, procedure
      begin
        if RestResponsePOST.StatusCode = 202 then // 202 Accepted bekliyoruz
          ShowMessage('Tarama başarıyla tetiklendi. Sistem veri toplamaya başladı.')
        else
          ShowMessage('Tarama başlatılamadı. API Dönüş Kodu: ' + IntToStr(RestResponsePOST.StatusCode));

        btnTaramaBaslat.Enabled := True; // İşlem bitince butonu tekrar aktif et
      end);

    except
      on E: Exception do
      begin
        TThread.Queue(nil, procedure
        begin
          ShowMessage('API bağlantı hatası oluştu: ' + E.Message);
          btnTaramaBaslat.Enabled := True;
        end);
      end;
    end;
  end);
end;

end.